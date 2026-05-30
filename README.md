# 🚀 git-copilot

> Stop writing "fixed stuff". Never stare at a blank commit message again.

[![GitHub stars](https://img.shields.io/github/stars/zhirenhun-stack/git-copilot?style=social)](https://github.com/zhirenhun-stack/git-copilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/zhirenhun-stack/git-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/zhirenhun-stack/git-copilot/actions/workflows/ci.yml)
[![Try it](https://img.shields.io/badge/Try%20it%E2%86%92-8A2BE2?logo=dev.to)](https://dev.to/z_z_c01afd7cf4c3764a2c73d/stop-writing-fixed-stuff-a-practical-guide-to-commit-messages-that-dont-suck-2g6c)

**git-copilot** reads your staged changes and generates a conventional commit message instantly. No AI, no API keys, no internet required — pure pattern matching.

```bash
$ git add .
$ git-copilot gen
✨ feat(api): add user routes and controller
3 file(s), +124/-15 lines
```

---

## Why?

- **5 seconds instead of 2 minutes** thinking of a message
- **Consistent format** — every commit follows conventional commits spec
- **Zero dependencies** — pure Python stdlib, works offline
- **Smart defaults** — infers type and scope from changed files

## Install

### One-liner (recommended)

```bash
curl -sL https://raw.githubusercontent.com/zhirenhun-stack/git-copilot/main/git-copilot > /usr/local/bin/git-copilot && chmod +x /usr/local/bin/git-copilot

# Or via install.sh
curl -sL https://raw.githubusercontent.com/zhirenhun-stack/git-copilot/main/install.sh | bash
```

### pip (coming soon)

```bash
pip install git-copilot
```

### From source

```bash
git clone https://github.com/zhirenhun-stack/git-copilot
cd git-copilot
pip install -e .
```

## Usage

```bash
git-copilot gen              # Generate from staged changes
git-copilot gen --type fix   # Force a type
git-copilot init             # Create config
git-copilot config           # View config
git-copilot gen | git commit -F -   # Use as commit
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

**Scope** is inferred from directory names: `api/`, `ui/`, `db/`, `auth/`, `config/`, etc.

## Real-world use

Hook it in:

```bash
#!/bin/bash
# .git/hooks/prepare-commit-msg
git-copilot gen > "$1"
```

Or VS Code keybindings — because `git commit -m "stuff"` is a crime.

---

## 📦 Git Commit Copilot Pro — Premium Templates Pack

The CLI above is **free and open-source (MIT)**. For teams and power users, the **Pro Templates Pack** adds:

| Feature | Free (CLI) | Pro (Gumroad) |
|---------|:----------:|:--------------:|
| Auto-detect type + scope | ✅ | ✅ |
| Conventional Commits spec | ✅ | ✅ |
| Configurable types & emojis | ✅ | ✅ |
| **Custom commit templates** | ❌ | ✅ |
| **Multi-line body templates** | ❌ | ✅ |
| **CI/CD-ready output formats** | ❌ | ✅ |
| **Breaking change tracking** | ❌ | ✅ |
| **Team convention presets** | ❌ | ✅ |
| **Issue tracker integration** | ❌ | ✅ |
| **Priority updates** | ❌ | ✅ |
| **Price** | **Free** | **$9.99** |

👉 **[Get the Pro Templates Pack on Gumroad](https://zhirenhun.gumroad.com/l/git-copilot-pro)**

## License

MIT — the CLI itself is and always will be free.
