# SDD Phase Rules

> Hooks automatically enforce these rules. See `.sdd/hooks/guard_phase.py` for implementation.

## CLI Commands

```bash
# Start a new feature — creates .task/[slug]/ with task files
python .sdd/sdd.py start "Feature name"

# Check current status
python .sdd/sdd.py status

# Advance through phases
python .sdd/sdd.py approve spec         # SPEC -> DESIGN
python .sdd/sdd.py approve design       # DESIGN -> TEST
python .sdd/sdd.py phase IMPLEMENT      # TEST -> IMPLEMENT (after red state confirmed)
python .sdd/sdd.py approve flow <file>  # Unlock one service/route file in IMPLEMENT
python .sdd/sdd.py reset flow           # Re-lock after flow changes
python .sdd/sdd.py phase REVIEW         # IMPLEMENT -> REVIEW (after all tests pass)
python .sdd/sdd.py done                 # Finish SDD

# View change log
python .sdd/sdd.py log
```

## Task file layout

Each feature gets its own directory under `.task/`:

```text
.task/
└── [feature_slug]/
    ├── task_spec.md          <- written in SPEC phase
    ├── task_design.md        <- written in DESIGN phase
    └── task_flow_summary.md  <- written per file in IMPLEMENT phase
```

Templates in `.sdd/spec.md`, `.sdd/design.md`, `.sdd/flow_summary.md` are **read-only references**.
The hook blocks any write to those files — always write to `.task/[slug]/` instead.

---

## Phase 0 — ANALYZE

| Item | Detail |
| ---- | ------ |
| **Purpose** | Understand requirements, assess complexity |
| **ALLOWED** | Read any file, write .sdd/state.json |
| **BLOCKED** | Edit/Write any source file |
| **Required output** | Complexity score (1-10), impact analysis, breakdown if score >= 6 |
| **Exit condition** | User confirms breakdown -> `sdd.py phase SPEC` |

---

## Phase 1 — SPEC

| Item | Detail |
| ---- | ------ |
| **Purpose** | Write behavioral specification, not implementation |
| **ALLOWED** | Read source files, write .sdd/spec.md |
| **BLOCKED** | Edit/Write `api/` or `frontend/` |
| **Required output** | spec.md: Behavior, API Contract, Business Rules, Edge Cases, Out of Scope |
| **Exit condition** | `sdd.py approve spec` |

---

## Phase 2 — DESIGN

| Item | Detail |
| ---- | ------ |
| **Purpose** | Define interfaces and contracts — no business logic |
| **ALLOWED** | Modify `api/schemas/`, `api/core/models/`, write .sdd/design.md |
| **BLOCKED** | `api/services/`, `api/interfaces/routes/`, `frontend/` |
| **Required output** | design.md with diff table, every change mapped to a spec clause |
| **Exit condition** | `sdd.py approve design` |

---

## Phase 3 — TEST

| Item | Detail |
| ---- | ------ |
| **Purpose** | Write tests before implementation (TDD) |
| **ALLOWED** | Write `api/test_*.py`, run tests |
| **BLOCKED** | Modify implementation to make tests pass |
| **Required output** | Every spec clause -> at least 1 test. Confirm all tests FAIL (red state) |
| **Exit condition** | User confirms red state -> `sdd.py phase IMPLEMENT` |

---

## Phase 4 — IMPLEMENT

| Item | Detail |
| ---- | ------ |
| **Purpose** | Implement code to pass all tests |
| **ALLOWED** | Modify `api/services/`, `api/interfaces/routes/`, `frontend/` |
| **BLOCKED** | Test files, `.sdd/spec.md`, `.sdd/design.md` |
| **Special rule** | Must write flow summary + get user approval before editing any service/route file |
| **Exit condition** | 100% tests pass -> `sdd.py phase REVIEW` |

### Flow Summary Protocol (required for every service/route file)

Before editing any file in `api/services/` or `api/interfaces/routes/`:

1. Claude reads the entire file
2. Claude writes a summary to `.sdd/flow_summary.md`:
   - Input / Output
   - Numbered execution steps
   - Observed issues (not yet fixed)
   - Exact planned changes
3. Claude displays the summary and **WAITS** for user confirmation
4. User runs: `python .sdd/sdd.py approve flow <file>`
5. Hook unlocks the file -> Claude may now edit it
6. After moving to the next file, approval resets automatically

---

## Phase 5 — REVIEW

| Item | Detail |
| ---- | ------ |
| **Purpose** | Code quality check, refactor if needed |
| **ALLOWED** | Read all changed files, run /simplify, edit per approved suggestions |
| **BLOCKED** | Test files, self-edit without user approval |
| **Required output** | Compliance checklist, issues labeled critical/minor |
| **Exit condition** | `sdd.py done` |

---

## State Machine

```text
NONE ----start----> ANALYZE
                       |
                  user confirms breakdown
                       |
                       v
                     SPEC
                       |
                  approve spec
                       |
                       v
                    DESIGN
                       |
                  approve design
                       |
                       v
                     TEST
                       |
                  red state OK
                       |
                       v
                  IMPLEMENT <---- flow summary loop
                       |          (per service/route file)
                  all tests pass
                       |
                       v
                    REVIEW
                       |
                      done
                       |
                       v
                     DONE   (hooks inactive)
```
