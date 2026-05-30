# Git Commit Convention Cheatsheet

## Format
```
<type>(<scope>): <subject>
```

## Types
| Type | Usage |
|------|-------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation |
| style | Formatting |
| refactor | Code restructure |
| perf | Performance |
| test | Tests |
| build | Build system |
| ci | CI/CD |
| chore | Maintenance |
| revert | Revert commit |

## Examples
```
feat(auth): add OAuth2 login
fix(api): handle null response on timeout
docs(readme): update installation guide
perf(db): add index on user.email
```

## Breaking Changes
Add `!` before colon:
```
feat!(api): remove v1 endpoints
```
Or in body: `BREAKING CHANGE: ...`
