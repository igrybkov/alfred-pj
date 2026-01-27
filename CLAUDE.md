# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Alfred workflow for quickly opening projects in their appropriate editor, terminal, or Finder. The workflow automatically detects the project type (Python, JavaScript, Go, Rust, PHP, Java, Obsidian) and opens it in the most suitable editor.

## Development Commands

```bash
# Link workflow to Alfred for development (creates symlink)
./bin/link

# Unlink workflow from Alfred
./bin/unlink

# Package workflow into .alfredworkflow file
./bin/package

# Set version (accepts: patch, minor, major, or specific version)
./bin/set-version patch
./bin/set-version 1.2.3

# Create a new release (must be on main branch with clean working tree)
./bin/release patch  # Bumps version, creates tag, pushes, creates GitHub release
```

## Architecture

- **main.py**: Core Python script with CLI commands using Click library
  - `list --paths <paths>`: Lists projects and returns Alfred JSON response
  - `editor --path <path>`: Determines the appropriate editor for a project
  - `record-selection --path <path>`: Records usage for sorting
  - `clear-usage`: Clears usage statistics

- **info.plist**: Alfred workflow configuration defining:
  - User-configurable variables (keyword, paths, editor preferences)
  - Workflow actions and modifier key bindings

- **lib/**: Bundled Click library (no external dependencies needed)

## Editor Detection Logic

The `Editors.determine_editor()` method uses this priority:
1. `.obsidian` directory → Obsidian
2. `.vscode` without `.idea` → VS Code
3. `pom.xml` → Java editors
4. `composer.json` or `*.php` → PHP editors
5. `*.ipynb` → Jupyter/Python editors
6. `requirements.txt`, `.venv`, or `*.py` → Python editors
7. `package.json` or `*.js` → JavaScript editors
8. `go.mod` or `*.go` → Go editors
9. `Cargo.toml` or `*.rs` → Rust editors
10. Fallback to `DEFAULT_EDITOR`

## Alfred Keyboard Shortcuts

- Default: Open in detected editor
- ⌥ (Option): Open in VS Code
- ⌃ (Control): Open GitHub page
- ⇧ (Shift): Open in Finder
- ⌘ (Command): Open in iTerm

## Configuration Variables

Environment variables for editor preferences (comma-separated, first available is used):
- `DEFAULT_EDITOR`: Fallback editor (default: `code`)
- `EDITORS_PHP`, `EDITORS_JAVA`, `EDITORS_PYTHON`, `EDITORS_JUPYTER`
- `EDITORS_JAVASCRIPT`, `EDITORS_GO`, `EDITORS_RUST`
