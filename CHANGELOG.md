# CHANGELOG

<!-- version list -->

## v1.1.5 (2026-02-14)

### Performance Improvements

- **cache**: Stagger editor availability checks with per-editor expiry
  ([`d776c7b`](https://github.com/igrybkov/alfred-pj/commit/d776c7b17a0ec8080f3b37dd1dd93816e4e8e09a))


## v1.1.4 (2026-02-12)

### Bug Fixes

- **ci**: Stop uploading info.plist and uv.lock as release assets
  ([`9dec360`](https://github.com/igrybkov/alfred-pj/commit/9dec360e0c78889705f4a428fa6667dc377deebf))


## v1.1.3 (2026-02-12)

### Bug Fixes

- **ci**: Install uv via optional-dep in PSR build_command
  ([`1d7a3d7`](https://github.com/igrybkov/alfred-pj/commit/1d7a3d78060ee6ddb0ed728a8bae9db5a24fd356))

### Chores

- Rename update command to install and add make targets
  ([`7fba34c`](https://github.com/igrybkov/alfred-pj/commit/7fba34c24ce0315dd57d76a0c133b038b4c3337f))

- Update uv.lock for v1.1.2
  ([`1b84ca6`](https://github.com/igrybkov/alfred-pj/commit/1b84ca60f07dbdd519c120e7c99a9e6a3a62db28))

- **lint**: Remove SIM112 noqa suppressions now globally ignored
  ([`a3f9b02`](https://github.com/igrybkov/alfred-pj/commit/a3f9b027dbf9ee3c847f314c5af092facfb5ee01))

### Continuous Integration

- Replace manual release workflow with python-semantic-release
  ([`cd6e238`](https://github.com/igrybkov/alfred-pj/commit/cd6e238c771391b17abae56a2c38059d8a6c0c54))

### Performance Improvements

- Add project/editor caches and parallelise list command
  ([`d1dec1b`](https://github.com/igrybkov/alfred-pj/commit/d1dec1bbb5277e9e3d7913b273af69f91dc305b0))

- **app.sh**: Skip uv sync when venv is already current
  ([`1e3b2e5`](https://github.com/igrybkov/alfred-pj/commit/1e3b2e5e306faecfa1253bf260e29d53e226e83e))


## v1.1.2 (2026-01-28)

### Bug Fixes

- **list**: Shorten home directory to ~ in subtitle display
  ([`9969635`](https://github.com/igrybkov/alfred-pj/commit/9969635302a3185513ca74ea28e8aff5d137e6f5))

- **release**: Regenerate uv.lock when bumping version
  ([`a681d0c`](https://github.com/igrybkov/alfred-pj/commit/a681d0c690de7c924fbdb8f091854e675a1ffdfb))

- **terminal**: Improve WezTerm launching on macOS
  ([`cb3d741`](https://github.com/igrybkov/alfred-pj/commit/cb3d741542e151173d8d869344b32a6ebacf5d0c))

- **terminal**: Use correct method to open Ghostty tabs on macOS
  ([`4518535`](https://github.com/igrybkov/alfred-pj/commit/451853568cf92bdc4164b57b7595c2bce112ea71))

- **tests**: Resolve ruff linting errors
  ([`0c395bf`](https://github.com/igrybkov/alfred-pj/commit/0c395bf68166cb6193a295f9f2efeb665210ef93))

### Chores

- **precommit**: Add pytest hook to run tests on commit
  ([`0bf5ec9`](https://github.com/igrybkov/alfred-pj/commit/0bf5ec9ef8e8b1dc0e313f72f2f7800eda5fa6d6))

- **precommit**: Add uv lock check and post-merge sync
  ([`f36c834`](https://github.com/igrybkov/alfred-pj/commit/f36c834a3a724c10c6f97933bf9636603d92e93e))

- **precommit**: Install post-merge hook by default
  ([`64feefe`](https://github.com/igrybkov/alfred-pj/commit/64feefe64ee0a63a99204547fc1c46bbe9ed4478))

### Refactoring

- **skill**: Restructure release-changelog to follow conventions
  ([`4349847`](https://github.com/igrybkov/alfred-pj/commit/434984763359f286d942a4b8b56c073263736999))

### Testing

- **terminal**: Update tests for new Ghostty and WezTerm implementations
  ([`4ecf54d`](https://github.com/igrybkov/alfred-pj/commit/4ecf54d10c3189b6a535052cebb3caa7b88e8c69))


## v1.1.1 (2026-01-27)

### Bug Fixes

- **list**: Skip hidden folders during project discovery
  ([`4be82cf`](https://github.com/igrybkov/alfred-pj/commit/4be82cfaad1738e9b61aac4f6bccc7d27257396b))

### Chores

- **pre-commit**: Restore sync-defaults hook with updated path
  ([`bca9942`](https://github.com/igrybkov/alfred-pj/commit/bca994200a7f6facd239fe36e0fb3146a6a4c9c2))

- **release**: Update sync-defaults import path and dependencies
  ([`21c7994`](https://github.com/igrybkov/alfred-pj/commit/21c79948d0de229f8b3cd1f061962e39ca169a9a))

### Continuous Integration

- Add GitHub workflow for tests and sync-defaults validation
  ([`98c8d69`](https://github.com/igrybkov/alfred-pj/commit/98c8d69255950dca0b23973ff8e7f0501906dd93))

- **release**: Add release link to workflow summary
  ([`ccc84a5`](https://github.com/igrybkov/alfred-pj/commit/ccc84a58719dbb9ec9c2ef7875fd5eb09288cb0e))

### Documentation

- Add release changelog skill for Claude
  ([`358d241`](https://github.com/igrybkov/alfred-pj/commit/358d24163ddc121c86503e98782c99e2ff310abf))

- Improve README with comprehensive documentation
  ([`5c76a04`](https://github.com/igrybkov/alfred-pj/commit/5c76a040d111142de78efccf062166f275c81d02))

### Features

- **list**: Add "Clear usage data" item to project list
  ([`4cbb617`](https://github.com/igrybkov/alfred-pj/commit/4cbb6176725fafc2dbb37557dbaa592a5908e799))

### Refactoring

- **cli**: Extract modules from monolithic cli.py
  ([`56ac0a0`](https://github.com/igrybkov/alfred-pj/commit/56ac0a012662bcbb562d91ec8e1dee8ee4b74438))

### Testing

- Add comprehensive test suite
  ([`6b10989`](https://github.com/igrybkov/alfred-pj/commit/6b1098969ffaa0e71faa033f16b2aea83defda54))

- Increase coverage to 99% with debug and clear-cache tests
  ([`8728959`](https://github.com/igrybkov/alfred-pj/commit/872895941d1c152c50c9ed8a79f1db3138c9e855))


## v1.1.0 (2026-01-27)

### Chores

- Update script type configuration in info.plist
  ([`2630ef0`](https://github.com/igrybkov/alfred-pj/commit/2630ef0f23916387423b2f89b9fd1a21005b3b00))

- **build**: Update package script for new project structure
  ([`5b8b8b3`](https://github.com/igrybkov/alfred-pj/commit/5b8b8b320525bcedf8383e899b8070c513ea3f2e))

### Continuous Integration

- Add GitHub Actions release workflow
  ([`8cce264`](https://github.com/igrybkov/alfred-pj/commit/8cce2644e6acef788ba5e4df896ea40aad01a5a5))

### Documentation

- Add CLAUDE.md for Claude Code guidance
  ([`f567b59`](https://github.com/igrybkov/alfred-pj/commit/f567b595dd4779166b375dd69c12a4e619004131))

### Features

- Add Python commands for all workflow actions
  ([`d2ad711`](https://github.com/igrybkov/alfred-pj/commit/d2ad7110ad2782ebc33f6adb1d31d754a3a3210d))

- Add uv wrapper script for isolated environment
  ([`e84a3c2`](https://github.com/igrybkov/alfred-pj/commit/e84a3c2cf2a0186c5f1902c28b1967306da1857b))

- **cli**: Add fallback paths for command lookup
  ([`a6e3fff`](https://github.com/igrybkov/alfred-pj/commit/a6e3ffff8e1d249ec12b5c492e8b3f270c672629))

- **release**: Sync version to both info.plist and pyproject.toml
  ([`df2e480`](https://github.com/igrybkov/alfred-pj/commit/df2e480072cfb89d1f8d3cce4a4296e4513c10f8))

### Refactoring

- Migrate to uv with src layout
  ([`a18b6fa`](https://github.com/igrybkov/alfred-pj/commit/a18b6fa12672c768ef580c67cb1a98bbabe5f90e))

- Use app.sh wrapper instead of direct python calls
  ([`d13e48c`](https://github.com/igrybkov/alfred-pj/commit/d13e48c164cff88bccb9576d388aea65c136b9b7))

- **release**: Replace bash scripts with Python CLI
  ([`d4cb6ec`](https://github.com/igrybkov/alfred-pj/commit/d4cb6ec8c851cdf3d83c36150d8cbcef961b5e06))


## v1.0.1 (2024-02-19)


## v1.0.0 (2024-01-18)
