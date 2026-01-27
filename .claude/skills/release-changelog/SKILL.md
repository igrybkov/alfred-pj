---
name: release-changelog
description: Generate and update release notes for GitHub releases
allowed-tools:
  - Bash(git tag:*)
  - Bash(git log:*)
  - Bash(gh release:*)
  - Read
  - Glob
---

# Release Changelog Skill

Generate release notes for GitHub releases.

## Format

```markdown
## Features

- **Feature name**: Brief description of what it does
- **Another feature**: Description

## Changes

- **Change name**: What changed and why
- **Breaking change** (if any): Description with migration notes

## Fixes

- **Bug description**: What was fixed

## Developer Experience

- Description of DX improvements (tooling, docs, etc.)

**Full Changelog**: https://github.com/{owner}/{repo}/compare/{previous_tag}...{new_tag}
```

## Guidelines

1. **Group by type**: Features, Changes, Fixes, Developer Experience (omit empty sections)
2. **Bold the key term**: Start each item with `**Term**:` followed by description
3. **Be concise**: One line per item, focus on user impact
4. **Use backticks** for code, commands, file names, and paths
5. **Include Full Changelog link** at the bottom comparing previous to new tag

## Example

```markdown
## Features

- **Multi-terminal support**: Ghostty, WezTerm, iTerm, Terminal.app (auto-detected)
- **Fallback PATH lookup**: Finds editors in `/opt/homebrew/bin`, `~/.local/bin`

## Changes

- **Migrated to `uv`** package manager with `src/` layout
- **Version synced** across `info.plist` and `pyproject.toml`

## Fixes

- **Editor detection**: Fixed false positives when `.idea` folder exists

**Full Changelog**: https://github.com/igrybkov/alfred-pj/compare/v1.0.1...v1.1.0
```

## Workflow

1. **Identify scope**
   - List recent tags with `git tag --sort=-creatordate | head -5`
   - Check existing release with `gh release view <tag>`
   - Get commits between tags with `git log <old_tag>..<new_tag> --oneline --no-merges`

2. **Generate changelog**
   - Group commits by type (features, fixes, changes, DX)
   - Write user-focused descriptions (what changed, not how)
   - Include Full Changelog link at the end

3. **Publish to GitHub**
   - Ask the user if they want to update the GitHub release
   - If yes, use `gh release edit <tag> --notes "..."` to update
