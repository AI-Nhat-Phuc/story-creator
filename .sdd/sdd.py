#!/usr/bin/env python3
"""
SDD Phase Manager CLI

Usage:
    python .sdd/sdd.py status
    python .sdd/sdd.py start "Feature name"
    python .sdd/sdd.py phase <PHASE>
    python .sdd/sdd.py approve spec
    python .sdd/sdd.py approve design
    python .sdd/sdd.py approve flow <file_path>
    python .sdd/sdd.py reset flow
    python .sdd/sdd.py done
    python .sdd/sdd.py log
"""
import json
import re
import sys
import os
from datetime import datetime

# Fix encoding on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

STATE_PATH = ".sdd/state.json"

PHASES = ["NONE", "ANALYZE", "SPEC", "DESIGN", "TEST", "IMPLEMENT", "REVIEW", "DONE"]


def task_slug(feature_name: str) -> str:
    """Convert feature name to a safe directory name."""
    slug = feature_name.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug[:50] or "task"


def phase_rules(task_dir: str) -> dict:
    return {
        "ANALYZE": [
            "ALLOWED  : Read any file, write .sdd/state.json",
            "BLOCKED  : Edit/Write any source file",
            "OUTPUT   : Complexity score (1-10), breakdown if score >= 6",
            f"NEXT     : User confirms breakdown -> python .sdd/sdd.py phase SPEC",
        ],
        "SPEC": [
            f"ALLOWED  : Read source files, write {task_dir}/task_spec.md",
            "BLOCKED  : Edit/Write api/ or frontend/",
            f"OUTPUT   : {task_dir}/task_spec.md — Behavior, API Contract, Business Rules, Edge Cases, Out of Scope",
            "NEXT     : python .sdd/sdd.py approve spec",
        ],
        "DESIGN": [
            f"ALLOWED  : Modify api/schemas/, api/core/models/, write {task_dir}/task_design.md",
            "BLOCKED  : api/services/, api/interfaces/routes/, frontend/",
            f"OUTPUT   : {task_dir}/task_design.md — diff table, every change mapped to spec clause",
            "NEXT     : python .sdd/sdd.py approve design",
        ],
        "TEST": [
            "ALLOWED  : Write api/test_*.py, run tests",
            "BLOCKED  : Modify implementation to make tests pass",
            "OUTPUT   : Every spec clause -> at least 1 test. Confirm red state (all FAIL)",
            "NEXT     : User confirms red state -> python .sdd/sdd.py phase IMPLEMENT",
        ],
        "IMPLEMENT": [
            "ALLOWED  : Modify api/services/, api/interfaces/routes/, frontend/",
            "BLOCKED  : Test files, task_spec.md, task_design.md",
            f"SPECIAL  : Must write {task_dir}/task_flow_summary.md + get approval before editing any service/route",
            "NEXT     : 100% tests pass -> python .sdd/sdd.py phase REVIEW",
        ],
        "REVIEW": [
            "ALLOWED  : Read changed files, run /simplify, edit per approved suggestions",
            "BLOCKED  : Test files, self-edit without user approval",
            "OUTPUT   : Compliance checklist, issues labeled critical/minor",
            "NEXT     : python .sdd/sdd.py done",
        ],
    }


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return default_state()


def default_state():
    return {
        "phase": "NONE",
        "current_feature": "",
        "task_dir": "",
        "breakdown": [],
        "spec_approved": False,
        "design_approved": False,
        "flow_summary_approved": False,
        "last_flow_file": "",
        "history": [],
    }


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def transition(state, new_phase):
    old_phase = state.get("phase", "NONE")
    state["history"].append({
        "from": old_phase,
        "to": new_phase,
        "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    state["phase"] = new_phase
    if new_phase == "IMPLEMENT":
        state["flow_summary_approved"] = False
        state["last_flow_file"] = ""
    return old_phase


# ── Task file templates ────────────────────────────────────────────────────────

SPEC_TEMPLATE = """\
# SPEC — {feature}

> **Status**: DRAFT
> **Phase**: SPEC
> **Date**: {date}

---

## Behavior

> Describe the behavior in natural language. NO code.

-

## API Contract

```text
METHOD /api/...
Body:     {{ ... }}
200:      {{ ... }}
4xx:      {{ "error": "...", ... }}
```

## Business Rules

1.

## Edge Cases

-

## Out of Scope

-
"""

DESIGN_TEMPLATE = """\
# DESIGN — {feature}

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: {date}

---

## Changed Files

| File | Change Type  | Maps to Spec Clause  |
| ---- | ------------ | -------------------- |
|      | NEW / MODIFY |                      |

## Schema / Interface Changes

```python
# api/schemas/...
```

## Model Changes

```python
# api/core/models/...
```

## New Method Signatures

```python
def new_method(arg1: type, arg2: type) -> ReturnType:
    raise NotImplementedError
```
"""

FLOW_SUMMARY_TEMPLATE = """\
# Flow Summary — {feature}

> **Status**: PENDING
> **File**:
> **Date**: {date}

---

## Current Flow

### Input

> Parameters, types.

### Execution Steps

1.
2.
3.

### Output

> Return value, side effects.

### Observed Issues

> Things Claude noticed but will NOT change unless asked.

- WARNING:

---

## Planned Changes

**Will add/modify:**
-

**Will NOT change:**
-
"""


def create_task_files(task_dir: str, feature: str):
    """Create task directory and initialize spec/design/flow_summary files."""
    os.makedirs(task_dir, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    ctx = {"feature": feature, "date": date}

    files = {
        "task_spec.md": SPEC_TEMPLATE.format(**ctx),
        "task_design.md": DESIGN_TEMPLATE.format(**ctx),
        "task_flow_summary.md": FLOW_SUMMARY_TEMPLATE.format(**ctx),
    }
    for fname, content in files.items():
        fpath = os.path.join(task_dir, fname).replace("\\", "/")
        if not os.path.exists(fpath):
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_status():
    state = load_state()
    phase = state.get("phase", "NONE")
    feature = state.get("current_feature") or "(not set)"
    task_dir = state.get("task_dir") or "(not set)"

    sep = "-" * 52
    print(f"\n{sep}")
    print(f"  SDD STATUS")
    print(sep)
    print(f"  Phase    : {phase}")
    print(f"  Feature  : {feature}")
    print(f"  Task dir : {task_dir}")

    if phase == "IMPLEMENT":
        fa = state.get("flow_summary_approved", False)
        lf = state.get("last_flow_file") or "(none)"
        print(f"  Flow OK  : {'APPROVED' if fa else 'PENDING'}")
        if fa:
            print(f"  Last file: {lf}")

    approvals = []
    if state.get("spec_approved"):
        approvals.append("spec")
    if state.get("design_approved"):
        approvals.append("design")
    if approvals:
        print(f"  Approved : {', '.join(approvals)}")

    if phase in phase_rules(task_dir):
        print(f"\n  Rules for {phase}:")
        for rule in phase_rules(task_dir)[phase]:
            print(f"    {rule}")

    history = state.get("history", [])
    if history:
        print(f"\n  History  :")
        for h in history[-5:]:
            print(f"    {h['at']}  {h['from']} -> {h['to']}")

    print(f"{sep}\n")


def cmd_start(feature_name):
    slug = task_slug(feature_name)
    tdir = f".task/{slug}"

    state = default_state()
    state["current_feature"] = feature_name
    state["task_dir"] = tdir
    state["phase"] = "ANALYZE"
    state["history"].append({
        "from": "NONE",
        "to": "ANALYZE",
        "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feature": feature_name,
    })

    create_task_files(tdir, feature_name)
    save_state(state)

    print(f"\nSDD started: '{feature_name}'")
    print(f"  Phase    : ANALYZE")
    print(f"  Task dir : {tdir}")
    print(f"\n  Task files created:")
    print(f"    {tdir}/task_spec.md")
    print(f"    {tdir}/task_design.md")
    print(f"    {tdir}/task_flow_summary.md")
    print(f"\n  Claude will now:")
    print(f"  1. Read the relevant codebase")
    print(f"  2. Score complexity (1-10)")
    print(f"  3. If score >= 6: propose a breakdown into SUBs")
    print(f"  4. Wait for your confirmation before moving to SPEC\n")


def cmd_phase(new_phase):
    new_phase = new_phase.upper()
    if new_phase not in PHASES:
        print(f"Invalid phase. Use: {', '.join(PHASES)}")
        sys.exit(1)
    state = load_state()
    old_phase = transition(state, new_phase)
    save_state(state)
    print(f"Phase: {old_phase} -> {new_phase}")


def cmd_approve(target, *args):
    state = load_state()
    task_dir = state.get("task_dir", ".task/task")

    if target == "spec":
        state["spec_approved"] = True
        transition(state, "DESIGN")
        save_state(state)
        print(f"Spec approved -> Phase: DESIGN")
        print(f"  Claude may now modify api/schemas/ and api/core/models/")
        print(f"  and write {task_dir}/task_design.md")

    elif target == "design":
        state["design_approved"] = True
        transition(state, "TEST")
        save_state(state)
        print(f"Design approved -> Phase: TEST")
        print(f"  Claude will now write tests (expect FAIL)")

    elif target == "flow":
        if not args:
            print("Missing file_path. Use: sdd.py approve flow <file_path>")
            sys.exit(1)
        file_path = args[0].replace("\\", "/")
        for prefix in [
            "c:/users/phucpn/projects/ai/ideas/story-creator/",
            "c:/Users/PhucPN/Projects/AI/Ideas/story-creator/",
        ]:
            if file_path.lower().startswith(prefix.lower()):
                file_path = file_path[len(prefix):]

        state["flow_summary_approved"] = True
        state["last_flow_file"] = file_path
        save_state(state)
        print(f"Flow summary approved for: {file_path}")
        print(f"  Claude may now implement changes to this file.")

    else:
        print(f"Unknown approve target: {target}")
        print(f"  Use: approve spec | approve design | approve flow <file>")
        sys.exit(1)


def cmd_reset(target):
    state = load_state()
    if target == "flow":
        state["flow_summary_approved"] = False
        state["last_flow_file"] = ""
        save_state(state)
        print("Flow summary approval reset.")
        print("  Claude must re-summarize the flow before continuing.")
    else:
        print(f"Unknown reset target: {target}")
        sys.exit(1)


def cmd_done():
    state = load_state()
    feature = state.get("current_feature", "")
    transition(state, "DONE")
    save_state(state)
    print(f"Feature '{feature}' DONE.")
    print(f"  SDD complete. Phase is DONE (hooks inactive).")


def cmd_log():
    log_path = ".sdd/changelog.log"
    if not os.path.exists(log_path):
        print("(no changes logged yet)")
        return
    with open(log_path, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[-30:]:
        print(line, end="")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        cmd_status()
    elif cmd == "start":
        if len(sys.argv) < 3:
            print('Missing feature name. Use: sdd.py start "Feature name"')
            sys.exit(1)
        cmd_start(sys.argv[2])
    elif cmd == "phase":
        if len(sys.argv) < 3:
            print(f"Missing phase. Use: sdd.py phase <{'|'.join(PHASES)}>")
            sys.exit(1)
        cmd_phase(sys.argv[2])
    elif cmd == "approve":
        if len(sys.argv) < 3:
            print("Missing target. Use: approve spec | approve design | approve flow <file>")
            sys.exit(1)
        cmd_approve(sys.argv[2], *sys.argv[3:])
    elif cmd == "reset":
        if len(sys.argv) < 3:
            print("Missing target. Use: reset flow")
            sys.exit(1)
        cmd_reset(sys.argv[2])
    elif cmd == "done":
        cmd_done()
    elif cmd == "log":
        cmd_log()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
