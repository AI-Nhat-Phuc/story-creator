#!/usr/bin/env python3
"""
SDD Change Logger Hook — PostToolUse (Edit | Write)

Logs each file change to .sdd/changelog.log with the current phase.
"""
import json
import sys
import os
from datetime import datetime

# Fix encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")


def load_phase():
    state_path = ".sdd/state.json"
    if not os.path.exists(state_path):
        return "NONE"
    try:
        with open(state_path, encoding="utf-8") as f:
            return json.load(f).get("phase", "NONE")
    except Exception:
        return "NONE"


def normalize(file_path):
    path = file_path.replace("\\", "/")
    for prefix in [
        "c:/users/phucpn/projects/ai/ideas/story-creator/",
        "c:/Users/PhucPN/Projects/AI/Ideas/story-creator/",
    ]:
        if path.lower().startswith(prefix.lower()):
            path = path[len(prefix):]
    return path


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return

    tool_name = data.get("tool_name", "unknown")
    tool_input = data.get("tool_input", {})
    file_path = normalize(tool_input.get("file_path", "unknown"))

    phase = load_phase()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_path = ".sdd/changelog.log"
    entry = f"[{timestamp}] [{phase:10s}] {tool_name:6s} -> {file_path}\n"

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


if __name__ == "__main__":
    main()
