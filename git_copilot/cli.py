#!/usr/bin/env python3
"""git-copilot — Smart conventional commit message generator.

Usage:
  git-copilot gen          Generate commit message from staged changes
  git-copilot gen --type   Force type (feat/fix/chore/...)
  git-copilot init         Create default config
  git-copilot config       Show current config
  git-copilot --help       This help
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "git-copilot"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "types": {
        "feat": {"description": "A new feature", "emoji": "✨"},
        "fix": {"description": "A bug fix", "emoji": "🐛"},
        "docs": {"description": "Documentation only", "emoji": "📝"},
        "style": {"description": "Code style (formatting, missing semicolons)", "emoji": "💄"},
        "refactor": {"description": "Code change that neither fixes a bug nor adds a feature", "emoji": "♻️"},
        "perf": {"description": "Performance improvement", "emoji": "⚡"},
        "test": {"description": "Adding or updating tests", "emoji": "✅"},
        "build": {"description": "Build system or external dependencies", "emoji": "📦"},
        "ci": {"description": "CI/CD configuration", "emoji": "👷"},
        "chore": {"description": "Other changes that don't modify src or test files", "emoji": "🔧"},
        "revert": {"description": "Reverts a previous commit", "emoji": "⏪"}
    },
    "max_subject_length": 72,
    "include_scope": True,
    "breaking_change_marker": "!"
}

# File type -> conventional commit type mapping
FILE_TYPE_MAP = {
    # Python
    ".py": "feat",
    # JavaScript/TypeScript
    ".js": "feat", ".ts": "feat", ".jsx": "feat", ".tsx": "feat",
    # Styles
    ".css": "style", ".scss": "style", ".less": "style",
    # Docs
    ".md": "docs", ".rst": "docs", ".txt": "docs",
    # Config
    ".json": "chore", ".yaml": "chore", ".yml": "chore", ".toml": "chore",
    ".ini": "chore", ".cfg": "chore",
    # Tests
    "_test.py": "test", "_spec.py": "test", ".test.js": "test", ".spec.js": "test",
    ".test.ts": "test", ".spec.ts": "test",
    # Build
    "Dockerfile": "build", ".dockerignore": "build",
    "Makefile": "build", "CMakeLists.txt": "build",
}

SCOPE_MAP = {
    "api": ["api", "route", "endpoint", "controller", "handler"],
    "ui": ["ui", "component", "page", "view", "template", "css", "style"],
    "db": ["db", "database", "migration", "sql", "query", "model"],
    "auth": ["auth", "login", "session", "permission", "role"],
    "config": ["config", "env", "setting", "conf"],
    "docs": ["doc", "readme", "changelog", "contributing"],
    "ci": ["ci", "github", "actions", "workflow", "docker"],
    "cli": ["cli", "command", "argument", "flag"],
}


def run_git(*args: str) -> str:
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""
    except subprocess.TimeoutExpired:
        return ""


def get_staged_diff() -> str:
    """Get the diff of staged changes."""
    return run_git("diff", "--cached", "--stat")


def get_staged_files() -> list[str]:
    """Get list of staged files."""
    output = run_git("diff", "--cached", "--name-only")
    return [f for f in output.split("\n") if f.strip()]


def detect_breaking_changes(files: list[str]) -> bool:
    """Check if staged changes include breaking changes."""
    for f in files:
        # Check if any migration or major API change files
        if "migration" in f.lower() or "breaking" in f.lower():
            return True
        # Check diff for breaking keywords
        diff = run_git("diff", "--cached", "-U0", "--", f)
        if "BREAKING CHANGE" in diff or "breaking change" in diff.lower():
            return True
    return False


def infer_type(files: list[str]) -> str:
    """Infer commit type from changed files."""
    has_src = False
    has_test = False
    has_docs = False
    has_config = False
    has_style = False
    has_build = False

    for f in files:
        lower = f.lower()
        ext = Path(f).suffix.lower()
        name = Path(f).name

        # Test detection
        if any(t in lower for t in ["test", "spec", "_test"]) or \
           any(t in name for t in ["test", "spec"]):
            has_test = True
            continue

        # Docs detection
        if ext in (".md", ".rst", ".txt"):
            has_docs = True
            continue

        # Config detection
        if ext in (".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"):
            has_config = True
            continue

        # Style detection
        if ext in (".css", ".scss", ".less"):
            has_style = True
            continue

        # Build detection
        if name in ("Dockerfile", "Makefile", "CMakeLists.txt") or \
           "/ci/" in lower or ".github/" in lower or ".gitlab/" in lower:
            has_build = True
            continue

        has_src = True

    if has_test and not has_src:
        return "test"
    if has_docs and not has_src and not has_test:
        return "docs"
    if has_config and not has_src:
        return "chore"
    if has_style:
        return "style"
    if has_build:
        return "build"
    if has_src:
        return "feat"

    return "chore"


def infer_scope(files: list[str]) -> str:
    """Infer scope from changed files."""
    file_text = " ".join(f.lower() for f in files)

    best_score = 0
    best_scope = ""

    for scope, keywords in SCOPE_MAP.items():
        score = sum(1 for kw in keywords if kw in file_text)
        if score > best_score:
            best_score = score
            best_scope = scope

    return best_scope


def summarize_changes(files: list[str], diff_stat: str) -> str:
    """Generate a concise summary of what changed."""
    changed_files = len(files)
    insertions = 0
    deletions = 0

    for line in diff_stat.split("\n"):
        parts = line.split()
        for i, p in enumerate(parts):
            if p.startswith("+"):
                try:
                    insertions += int(p.replace("+", "").replace(",", ""))
                except ValueError:
                    pass
            elif p.startswith("-"):
                try:
                    deletions += int(p.replace("-", "").replace(",", ""))
                except ValueError:
                    pass

    return f"{changed_files} file(s), +{insertions}/-{deletions} lines"


def generate_message(
    files: list[str],
    diff_stat: str,
    force_type: str = "",
    config: dict = None,
) -> str:
    """Generate a conventional commit message."""
    if config is None:
        config = load_config()

    types_config = config["types"]

    # Determine type
    commit_type = force_type if force_type else infer_type(files)
    if commit_type not in types_config:
        commit_type = "chore"

    # Determine scope
    scope = ""
    if config.get("include_scope"):
        s = infer_scope(files)
        if s:
            scope = f"({s})"

    # Detect breaking changes
    breaking = detect_breaking_changes(files)
    breaking_marker = config.get("breaking_change_marker", "!") if breaking else ""

    # Generate subject from file changes
    subject = generate_subject(commit_type, files, diff_stat)

    max_len = config.get("max_subject_length", 72)
    if len(subject) > max_len:
        subject = subject[: max_len - 3] + "..."

    # Build the message
    emoji = types_config.get(commit_type, {}).get("emoji", "")
    header = f"{commit_type}{scope}{breaking_marker}: {subject}"
    if emoji:
        header = f"{emoji} {header}"

    # Body with summary
    summary = summarize_changes(files, diff_stat)
    body = f"\n\n{summary}"

    if breaking:
        body += "\n\nBREAKING CHANGE: This commit introduces a breaking API change."

    return f"{header}{body}"


def generate_subject(commit_type: str, files: list[str], diff_stat: str) -> str:
    """Generate a human-readable subject line from changed files."""
    file_names = [Path(f).name for f in files[:5]]

    if commit_type == "feat":
        verbs = ["add", "implement", "introduce", "support"]
        # Pick a good verb
        changed_dirs = set(Path(f).parent.name for f in files if Path(f).parent.name)
        if "api" in str(changed_dirs) or "route" in str(changed_dirs):
            return f"add {', '.join(file_names[:3])}"
        return f"{verbs[0]} {', '.join(file_names[:3])}"

    if commit_type == "fix":
        return f"fix {', '.join(file_names[:3])}"

    if commit_type == "docs":
        return f"update {', '.join(file_names[:3])}"

    if commit_type == "refactor":
        return f"refactor {', '.join(file_names[:3])}"

    if commit_type == "test":
        test_files = [f for f in file_names if "test" in f.lower() or "spec" in f.lower()]
        if test_files:
            return f"add tests for {', '.join(test_files[:3])}"
        return f"update tests"

    if commit_type == "chore":
        return f"update {', '.join(file_names[:3])}"

    return f"update {', '.join(file_names[:3])}"


def load_config() -> dict:
    """Load configuration from file, or create default."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def cmd_init() -> None:
    """Initialize git-copilot config."""
    save_config(DEFAULT_CONFIG)
    print(f"✅ Config created at {CONFIG_FILE}")


def cmd_config() -> None:
    """Show current configuration."""
    config = load_config()
    print(json.dumps(config, indent=2))


def cmd_gen(force_type: str = "") -> None:
    """Generate a commit message from staged changes."""
    files = get_staged_files()

    if not files:
        print("⚠️  No staged changes found. Stage your changes first:")
        print("   git add <files>")
        sys.exit(1)

    diff_stat = get_staged_diff()
    config = load_config()

    message = generate_message(files, diff_stat, force_type, config)
    print(message)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="git-copilot — Smart conventional commit message generator",
    )
    parser.add_argument("--version", action="version", version="1.0.0")

    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("gen", help="Generate commit message from staged changes")
    gen.add_argument("--type", "-t", help="Force commit type")

    sub.add_parser("init", help="Create default config")
    sub.add_parser("config", help="Show current config")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "config":
        cmd_config()
    elif args.command == "gen":
        cmd_gen(force_type=args.type or "")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
