# DESIGN — description generation enhancement

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-04-10

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
| ---- | ----------- | ------------------- |
| `api/ai/prompts.py` | MODIFY | Spec §"Enhance existing" mode |
| `api/interfaces/routes/gpt_routes.py` | MODIFY | Spec §"API Contract", §"Business Rules" |
| `frontend/src/pages/WorldsPage.jsx` | MODIFY | Spec §"Behavior" |

## Schema / Interface Changes

No `api/schemas/` or `api/core/models/` changes needed.
The `/api/gpt/generate-description` endpoint uses `request.json` directly — `existing_description` is a new optional field, backward-compatible.

## New Prompt Template (api/ai/prompts.py)

```python
API_WORLD_DESCRIPTION_ENHANCE_TEMPLATE = """You have an existing description for a {world_type} world named '{world_name}':

{existing_description}

Expand and enrich this description with more detail.

Requirements:
- Keep the original ideas and tone intact
- Add: deeper geographical features, cultural nuances, unique world elements
- Length: approximately 150-200 words total
- Natural and vivid writing style

Return ONLY the world description content, NO titles, notes, explanations or any other text."""
```

## Route Logic (api/interfaces/routes/gpt_routes.py)

Inside `generate_description()` for `gen_type == 'world'`:
```python
existing_description = data.get('existing_description', '').strip()
if existing_description:
    prompt = PromptTemplates.API_WORLD_DESCRIPTION_ENHANCE_TEMPLATE.format(
        world_type=world_type,
        world_name=world_name,
        existing_description=existing_description
    )
else:
    prompt = PromptTemplates.API_WORLD_DESCRIPTION_TEMPLATE.format(
        world_type=world_type,
        world_name=world_name
    )
```

## Frontend Change (frontend/src/pages/WorldsPage.jsx)

In `generateDescriptionWithGPT()`, add `existing_description` to the payload:
```js
const response = await gptAPI.generateDescription({
    type: 'world',
    world_name: formData.name,
    world_type: formData.world_type,
    existing_description: formData.description   // NEW — empty string when no existing text
})
```
