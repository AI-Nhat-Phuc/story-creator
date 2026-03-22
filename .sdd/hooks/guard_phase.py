#!/usr/bin/env python3
"""
SDD Phase Guard Hook — PreToolUse (Edit | Write)

Reads JSON from stdin, blocks Edit/Write if it violates current phase rules.

Output: JSON {"decision": "block", "reason": "..."} to stdout to block.
Exit 0 without output = allow.
"""
import json
import sys
import os

# Fix encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

# Templates in .sdd/ are NEVER writable — task files live in .task/
SDD_TEMPLATES = {".sdd/spec.md", ".sdd/design.md", ".sdd/flow_summary.md"}


def load_state():
    state_path = ".sdd/state.json"
    if not os.path.exists(state_path):
        return {"phase": "NONE", "task_dir": ""}
    try:
        with open(state_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"phase": "NONE", "task_dir": ""}


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)


def allow():
    sys.exit(0)


def normalize(file_path):
    path = file_path.replace("\\", "/").lstrip("/")
    for prefix in [
        "c:/users/phucpn/projects/ai/ideas/story-creator/",
        "c:/Users/PhucPN/Projects/AI/Ideas/story-creator/",
    ]:
        if path.lower().startswith(prefix.lower()):
            path = path[len(prefix):]
    return path


def is_source(path):
    return path.startswith("api/") or path.startswith("frontend/")


def is_test_file(path):
    return (
        path.startswith("api/test_")
        or "/test_" in path
        or path.endswith("_test.py")
    )


def is_schema_or_model(path):
    return "api/schemas/" in path or "api/core/models/" in path


def is_service_or_route(path):
    return "api/services/" in path or "api/interfaces/routes/" in path


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        allow()
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        allow()
        return

    file_path = normalize(file_path)

    state = load_state()
    phase = state.get("phase", "NONE").upper()
    task_dir = state.get("task_dir", "").rstrip("/")

    # No active SDD process
    if phase in ("NONE", "DONE", ""):
        allow()
        return

    # ── Template files are ALWAYS blocked ─────────────────────────────────────
    if file_path in SDD_TEMPLATES:
        block(
            f"[{phase}] '{file_path}' is a template — do not modify it.\n"
            f"  Write task files to '{task_dir}/' instead:\n"
            f"    {task_dir}/task_spec.md\n"
            f"    {task_dir}/task_design.md\n"
            f"    {task_dir}/task_flow_summary.md"
        )

    # ── .sdd/ other files (state.json, hooks, etc.) — always allowed ──────────
    if file_path.startswith(".sdd/"):
        allow()
        return

    # ── .task/ files — check per phase ────────────────────────────────────────
    if file_path.startswith(".task/"):
        task_spec = f"{task_dir}/task_spec.md"
        task_design = f"{task_dir}/task_design.md"

        # In IMPLEMENT/REVIEW: protect spec and design from modification
        if phase in ("IMPLEMENT", "REVIEW"):
            if file_path == task_spec:
                block(
                    f"[{phase}] Cannot modify {task_spec}.\n"
                    f"  task_spec.md is immutable after approval."
                )
            if file_path == task_design:
                block(
                    f"[{phase}] Cannot modify {task_design}.\n"
                    f"  task_design.md is immutable after approval."
                )
        allow()
        return

    # ── Source files — phase rules ─────────────────────────────────────────────

    # ANALYZE — read only
    if phase == "ANALYZE":
        if is_source(file_path):
            block(
                "[ANALYZE] Cannot modify source files.\n"
                "  This phase is READ-ONLY — analyze only.\n"
                "  -> Write results to .sdd/state.json, then wait for user to confirm breakdown."
            )

    # SPEC — only task_spec.md allowed (already handled above in .task/ block)
    elif phase == "SPEC":
        if is_source(file_path):
            block(
                "[SPEC] Cannot modify source files.\n"
                f"  Write the specification to '{task_dir}/task_spec.md'.\n"
                "  -> Complete the spec, then: python .sdd/sdd.py approve spec"
            )

    # DESIGN — only schemas and models
    elif phase == "DESIGN":
        if is_source(file_path) and not is_schema_or_model(file_path):
            block(
                "[DESIGN] Only allowed to modify:\n"
                "  - api/schemas/\n"
                "  - api/core/models/\n"
                f"  '{file_path}' is out of DESIGN scope.\n"
                "  -> No business logic, routes, or frontend changes allowed."
            )

    # TEST — only test files
    elif phase == "TEST":
        if is_source(file_path) and not is_test_file(file_path):
            block(
                "[TEST] Only allowed to write test files (api/test_*.py).\n"
                f"  '{file_path}' is an implementation file.\n"
                "  -> Write tests first, let them FAIL (red state).\n"
                "  -> User must confirm 'red state OK' before moving to IMPLEMENT."
            )

    # IMPLEMENT — no tests, flow summary required for service/route
    elif phase == "IMPLEMENT":
        if is_test_file(file_path):
            block(
                "[IMPLEMENT] Cannot modify test files.\n"
                "  Tests are immutable in this phase.\n"
                "  -> Implement code to make tests pass — do not change the tests."
            )

        if is_service_or_route(file_path):
            flow_approved = state.get("flow_summary_approved", False)
            last_flow_file = state.get("last_flow_file", "").replace("\\", "/")
            flow_summary_path = f"{task_dir}/task_flow_summary.md"

            if not flow_approved or last_flow_file != file_path:
                block(
                    f"[IMPLEMENT] Must summarize the flow logic before modifying '{file_path}'.\n\n"
                    f"  Required steps:\n"
                    f"  1. Read the entire file '{file_path}'\n"
                    f"  2. Write a flow summary to '{flow_summary_path}'\n"
                    f"  3. Show the summary to the user and WAIT for confirmation\n"
                    f"  4. Run: python .sdd/sdd.py approve flow {file_path}\n"
                    f"  5. Then you may edit this file."
                )

    # REVIEW — no test files
    elif phase == "REVIEW":
        if is_test_file(file_path):
            block(
                "[REVIEW] Cannot modify test files.\n"
                "  -> Only refactor implementation code."
            )

    allow()


if __name__ == "__main__":
    main()
