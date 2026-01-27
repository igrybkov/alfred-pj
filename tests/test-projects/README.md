# Test Projects

These are minimal project structures for testing the editor detection UI in Alfred.

## Usage

Add this directory to your `paths` configuration in the Alfred workflow:

```
~/Projects/alfred-pj/tests/test-projects
```

Then invoke Alfred with `pj` to see all test projects and verify each one shows the correct editor icon.

## Projects

| Directory | Detection Type | Expected Editor |
|-----------|---------------|-----------------|
| `obsidian-vault` | Obsidian | Obsidian |
| `vscode-project` | VS Code | VS Code |
| `java-maven-project` | Java (Maven) | IntelliJ IDEA |
| `java-gradle-project` | Java (Gradle) | IntelliJ IDEA |
| `php-project` | PHP | PHPStorm |
| `jupyter-project` | Jupyter | PyCharm |
| `python-project` | Python | PyCharm |
| `typescript-project` | TypeScript | WebStorm |
| `javascript-project` | JavaScript | WebStorm |
| `go-project` | Go | GoLand |
| `rust-project` | Rust | RustRover |
| `ruby-project` | Ruby | RubyMine |
| `cpp-cmake-project` | C++ (CMake) | CLion |
| `cpp-makefile-project` | C (Makefile) | CLion |

Note: The actual editor shown depends on which editors are installed on your system. The workflow uses the first available editor from the configured list.
