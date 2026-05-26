# 🚀 git-copilot

> Stop writing "fixed stuff". Never stare at a blank commit message again.

**git-copilot** reads your staged changes and generates a conventional commit message instantly. No AI, no API keys, no internet required — pure pattern matching.

```bash
$ git add .
$ git-copilot gen
✨ feat(api): add user routes and controller
3 file(s), +124/-15 lines
```

## Why?

- **5 seconds instead of 2 minutes** thinking of a message
- **Consistent format** — every commit follows conventional commits spec
- **Zero dependencies** — pure Python stdlib, works offline
- **Smart defaults** — infers type and scope from changed files

## Install

```bash
# pip install git-copilot
pip install git-copilot

# Or install from source
git clone https://github.com/zhirenhun-stack/git-copilot
cd git-copilot
pip install -e .
```

## Usage

```bash
# Generate message from staged changes
git-copilot gen

# Force a specific commit type
git-copilot gen --type fix

# Init config (~/.config/git-copilot/config.json)
git-copilot init

# View current config
git-copilot config

# Use directly as git commit
git-copilot gen | git commit -F -
```

## How it works

| File changed → | Auto-detected type |
|----------------|-------------------|
| `src/*.py` | feat |
| `src/*.js` | feat |
| `_test.py` / `spec.js` | test |
| `README.md` / `docs/*` | docs |
| `Dockerfile` / `ci/*` | build |
| `.css` / `.scss` | style |
| `config.json` / `.yaml` | chore |

And **scope** is inferred from directory names: `api/`, `ui/`, `db/`, `auth/`, `config/`, etc.

## Configuration

```json
{
  "types": {
    "feat": { "description": "A new feature", "emoji": "✨" },
    "fix": { "description": "A bug fix", "emoji": "🐛" },
    ...
  },
  "max_subject_length": 72,
  "include_scope": true,
  "breaking_change_marker": "!"
}
```

## Real-world use

Drop this in your git hooks:

```bash
#!/bin/bash
# .git/hooks/prepare-commit-msg
git-copilot gen > "$1"
```

Or use as a VS Code keybinding — because `git commit -m "stuff"` is a crime.

## License

MIT
