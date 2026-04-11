# Flow Summary — backend security hardening

> **Status**: PENDING
> **File**: `api/interfaces/routes/gpt_routes.py` (+ minor `api/schemas/gpt_schemas.py`)
> **Date**: 2026-04-11
> **SUB**: 3 (validation + debug print) + 4 (error sanitization) + 5 (results rate limit)

---

## Current Flow

### `create_gpt_bp(backend, gpt_results, storage, flush_data, limiter)`

Current routes and decorators:

| Route | Decorators | Notes |
|---|---|---|
| `POST /api/gpt/generate-description` | `@_gpt_limit @token_required` | reads `request.json` raw; has `print(f"[DEBUG] ...")` on lines 128 and 174; background thread swallows exception as `str(e)` into `gpt_results[task_id]['result']` |
| `POST /api/gpt/analyze` | `@_gpt_limit @token_required` | reads `request.json` raw; same `str(e)` leak in `on_error` callback |
| `GET /api/gpt/results/<task_id>` | none | no rate limit |
| `POST /api/gpt/batch-analyze-stories` | `@_gpt_limit @token_required` | reads `request.json` raw; same `str(e)` leak |
| `GET /api/gpt/tasks` | none | list — unchanged |
| `POST /api/gpt/paraphrase` | `@_gpt_limit @token_required @validate_request(GptParaphraseSchema)` | already fully protected; `except Exception as e: raise ExternalServiceError('GPT', str(e))` leaks error text |

### Observed Issues

- **Issue A (SUB-3)**: `gpt_generate_description` reads `request.json` directly — no length bounds, no type enum validation, no prompt-injection sanitization. Attackers can smuggle `system:` hints into `world_name`/`characters` and try to reshape the GPT prompt.
- **Issue B (SUB-3)**: `gpt_analyze` same problem — raw `request.json`.
- **Issue C (SUB-3 debug prints)**: Lines 128 and 174 have `print(f"[DEBUG] Generated ... description: {description[:100]}...")`. Test `TestDebugPrintRemoved` asserts the literal `print(f"[DEBUG]` string must not appear in source.
- **Issue D (SUB-4 error leak)**: The background-thread `except Exception as e: gpt_results[task_id] = {'status': 'error', 'result': str(e)}` leaks raw OpenAI exception strings (API keys, internal tracebacks) into the HTTP response body that clients poll via `/api/gpt/results/<task_id>`. Same pattern in `gpt_analyze.on_error` and `gpt_batch_analyze_stories.batch_analyze`. `gpt_paraphrase` also raises `ExternalServiceError('GPT', str(e))` — also leaky.
- **Issue E (SUB-5 rate limit gap)**: `gpt_get_results` is a public polling endpoint with no rate limit — cheap side-channel for a task_id brute force, and can DOS the mongomock storage layer.
- **Issue F (schema field mismatch)**: `GptAnalyzeSchema` currently defines `story_content` but the frontend sends `story_description` (verified via `frontend/src/containers/StoryDetailContainer.jsx:140`, `WorldsPage.jsx:187`). Also missing `story_genre` and `world_type`. Needs additional fields to avoid breaking the frontend when `@validate_request` is applied.

---

## Planned Changes

### Change 1 — Fix `GptAnalyzeSchema` fields to match frontend (SUB-3 pre-req)

**File**: `api/schemas/gpt_schemas.py`

Add `story_description`, `story_genre`, `world_type` as new optional fields on `GptAnalyzeSchema` and extend the `_sanitize` post_load to sanitize the new string fields. Keep `story_content` as-is so existing unit tests (`test_story_content_max_10000`, `test_sanitizer_applied`) stay green.

```python
class GptAnalyzeSchema(Schema):
    world_description = fields.Str(load_default='', validate=validate.Length(max=10000))
    story_content     = fields.Str(load_default='', validate=validate.Length(max=10000))
    story_description = fields.Str(load_default='', validate=validate.Length(max=10000))
    world_name        = fields.Str(load_default='', validate=validate.Length(max=200))
    story_title       = fields.Str(load_default='', validate=validate.Length(max=200))
    story_genre       = fields.Str(load_default='', validate=validate.Length(max=50))
    world_type        = fields.Str(load_default='', validate=validate.Length(max=50))

    @post_load
    def _sanitize(self, data, **_kwargs):
        for key in (
            'world_description', 'story_content', 'story_description',
            'world_name', 'story_title', 'story_genre', 'world_type',
        ):
            if key in data:
                data[key] = _sanitize_prompt_text(data[key])
        return data
```

### Change 2 — Wire `@validate_request(GenerateDescriptionSchema)` on `gpt_generate_description` (SUB-3)

Import at top:
```python
from schemas.gpt_schemas import (
    GptParaphraseSchema,
    GenerateDescriptionSchema,
    GptAnalyzeSchema,
)
```

Decorator stack:
```python
@gpt_bp.route('/api/gpt/generate-description', methods=['POST'])
@_gpt_limit
@token_required
@validate_request(GenerateDescriptionSchema)
def gpt_generate_description():
    ...
    data = request.validated_data  # instead of request.json
```

Route body already branches on `data.get('type')` so existing logic is compatible.

### Change 3 — Replace `print(f"[DEBUG] ...")` with `logger.debug(...)` (SUB-3)

Add at top of file:
```python
import logging
logger = logging.getLogger(__name__)
```

Replace line 128:
```python
logger.debug("Generated world description (%d chars)", len(description))
```
Replace line 174 similarly. No description content is logged — only length — to avoid broadcasting GPT output into server logs.

### Change 4 — Wire `@validate_request(GptAnalyzeSchema)` on `gpt_analyze` (SUB-3)

```python
@gpt_bp.route('/api/gpt/analyze', methods=['POST'])
@_gpt_limit
@token_required
@validate_request(GptAnalyzeSchema)
def gpt_analyze():
    ...
    data = request.validated_data
    world_description = data.get('world_description', '')
    story_description = data.get('story_description', '') or data.get('story_content', '')
    world_type        = data.get('world_type', '') or 'fantasy'
    story_title       = data.get('story_title', '')
    story_genre       = data.get('story_genre', '')
```

The `story_description or story_content` fallback means either field is accepted, preserving compatibility with both the frontend (`story_description`) and the schema unit tests (`story_content`).

### Change 5 — Sanitize GPT background-thread error (SUB-4)

In `gpt_generate_description.generate_description`:

```python
except Exception as e:
    logger.error("GPT generate-description failed", exc_info=True)
    gpt_results[task_id] = {
        'status': 'error',
        'result': 'GPT request failed',
    }
```

In `gpt_analyze.on_error`:

```python
def on_error(error):
    logger.error("GPT analyze failed: %s", error, exc_info=True)
    gpt_results[task_id] = {
        'status': 'error',
        'result': 'GPT request failed',
    }
```

In `gpt_batch_analyze_stories.batch_analyze.except`:

```python
except Exception as e:
    logger.error("GPT batch-analyze failed", exc_info=True)
    gpt_results[task_id] = {
        'status': 'error',
        'result': 'GPT request failed',
    }
```

In `gpt_paraphrase.except`:

```python
except Exception as e:
    logger.error("GPT paraphrase failed", exc_info=True)
    raise ExternalServiceError('GPT', 'GPT request failed')
```

All original error details still reach the server log via `exc_info=True` but never land in `gpt_results[task_id]['result']` (which is returned verbatim to HTTP clients polling `/api/gpt/results/<task_id>`).

### Change 6 — Add `@_gpt_limit` to `gpt_get_results` (SUB-5)

```python
@gpt_bp.route('/api/gpt/results/<task_id>', methods=['GET'])
@_gpt_limit
def gpt_get_results(task_id):
    ...
```

No `@token_required` — per spec, `/api/gpt/results/<task_id>` stays public because the UUID4 task_id is unguessable, but it now counts against the GPT rate limit.

### NOT changing

- `gpt_list_tasks` (unchanged — already reads from `gpt_results` dict).
- `gpt_paraphrase` validation decorator (already wired).
- Route bodies that don't touch error handling or validation.
- Business logic of description generation, analysis, and batch analysis.

---

## Backward Compatibility

- **Frontend `world_description + world_type` for generate-description**: already matches `GenerateDescriptionSchema`; zero change.
- **Frontend `story_description` + `story_genre` + `story_title` for analyze**: newly accepted fields on `GptAnalyzeSchema` preserve the exact request shape. The schema's `story_content` field is retained so the design-phase unit tests remain green.
- **Error-result polling**: clients that checked `result` for a specific error message now see the generic `"GPT request failed"` string. Frontend code inspected during ANALYZE phase displays the error as a toast — the message string is shown verbatim and has no logic branch on error text. No breakage.
- **`@_gpt_limit` on `gpt_get_results`**: at a frontend polling rate of once per 2 seconds, a single task completion (~5s) fires ~3 polls — well under the 10/min cap. Two concurrent polls fire ~6/min total. Safe for interactive use.

---

## Test coverage wired

- `TestGptRouteValidationWired.test_oversize_world_name_rejected` → will pass
- `TestGptRouteValidationWired.test_invalid_type_rejected` → will pass
- `TestDebugPrintRemoved.test_no_debug_print_in_gpt_routes` → will pass
- `TestGptErrorSanitization.test_openai_error_not_leaked_in_response` → will pass
- `TestGptResultsRateLimit.test_gpt_get_results_decorated` → will pass
- `TestGptAnalyzeSchema.*` → stay green (story_content field preserved)
- `TestPromptInjectionSanitizer.*` → stay green

Expected count flip: 5 → ~1 failing after this file is committed (only mongo_storage whitelist remains).
