"""Shared test fixtures for alfred-pj tests."""

import pytest


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    project = tmp_path / "test_project"
    project.mkdir()
    return project


@pytest.fixture
def python_project(temp_project):
    """Create a Python project structure."""
    (temp_project / "pyproject.toml").touch()
    return temp_project


@pytest.fixture
def javascript_project(temp_project):
    """Create a JavaScript project structure."""
    (temp_project / "package.json").touch()
    return temp_project


@pytest.fixture
def typescript_project(temp_project):
    """Create a TypeScript project structure."""
    (temp_project / "tsconfig.json").touch()
    return temp_project


@pytest.fixture
def go_project(temp_project):
    """Create a Go project structure."""
    (temp_project / "go.mod").touch()
    return temp_project


@pytest.fixture
def rust_project(temp_project):
    """Create a Rust project structure."""
    (temp_project / "Cargo.toml").touch()
    return temp_project


@pytest.fixture
def java_maven_project(temp_project):
    """Create a Java Maven project structure."""
    (temp_project / "pom.xml").touch()
    return temp_project


@pytest.fixture
def java_gradle_project(temp_project):
    """Create a Java Gradle project structure."""
    (temp_project / "build.gradle").touch()
    return temp_project


@pytest.fixture
def php_project(temp_project):
    """Create a PHP project structure."""
    (temp_project / "composer.json").touch()
    return temp_project


@pytest.fixture
def jupyter_project(temp_project):
    """Create a Jupyter notebook project structure."""
    (temp_project / "notebook.ipynb").touch()
    return temp_project


@pytest.fixture
def obsidian_vault(temp_project):
    """Create an Obsidian vault structure."""
    (temp_project / ".obsidian").mkdir()
    return temp_project


@pytest.fixture
def vscode_project(temp_project):
    """Create a VS Code project structure."""
    (temp_project / ".vscode").mkdir()
    return temp_project


@pytest.fixture
def idea_project(temp_project):
    """Create an IntelliJ IDEA project structure."""
    (temp_project / ".idea").mkdir()
    return temp_project


@pytest.fixture
def ruby_project(temp_project):
    """Create a Ruby project structure."""
    (temp_project / "Gemfile").touch()
    return temp_project


@pytest.fixture
def cpp_project(temp_project):
    """Create a C++ project structure."""
    (temp_project / "CMakeLists.txt").touch()
    return temp_project


@pytest.fixture
def mock_env(monkeypatch):
    """Helper to mock environment variables."""

    def _mock(**kwargs):
        for key, value in kwargs.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, value)

    return _mock


@pytest.fixture
def temp_usage_dir(tmp_path, monkeypatch):
    """Set up temporary usage data directory."""
    data_dir = tmp_path / "alfred_data"
    data_dir.mkdir()
    monkeypatch.setenv("alfred_workflow_data", str(data_dir))
    return data_dir


@pytest.fixture
def projects_dir(tmp_path):
    """Create a directory with multiple project subdirectories."""
    projects = tmp_path / "projects"
    projects.mkdir()

    # Create various project types
    python_proj = projects / "my-python-app"
    python_proj.mkdir()
    (python_proj / "pyproject.toml").touch()

    js_proj = projects / "my-js-app"
    js_proj.mkdir()
    (js_proj / "package.json").touch()

    go_proj = projects / "my-go-app"
    go_proj.mkdir()
    (go_proj / "go.mod").touch()

    return projects
