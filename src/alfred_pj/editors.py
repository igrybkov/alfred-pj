"""Editor detection and configuration."""

import glob
import os

from alfred_pj.utils import logger, which

# Detection rules - order matters (first match wins)
DETECTORS = [
    # Obsidian vault
    {
        "name": "obsidian",
        "dirs": [".obsidian"],
        "editors": ["obsidian"],
    },
    # # VS Code project (explicit .vscode, no .idea)
    {
        "name": "vscode",
        "dirs": [".vscode"],
        "exclude_dirs": [".idea"],
        "editors": ["code"],
    },
    # Java - Maven, Gradle, Ant
    {
        "name": "java",
        "files": ["pom.xml", "build.gradle", "build.gradle.kts", "build.xml"],
        "env": "EDITORS_JAVA",
        "editors": ["idea", "code"],
    },
    # PHP
    {
        "name": "php",
        "files": ["composer.json"],
        "globs": ["*.php"],
        "env": "EDITORS_PHP",
        "editors": ["phpstorm", "idea", "code"],
    },
    # Jupyter notebooks
    {
        "name": "jupyter",
        "globs": ["*.ipynb"],
        "env": ["EDITORS_JUPYTER", "EDITORS_PYTHON"],
        "editors": ["pycharm", "idea", "code"],
    },
    # Python
    {
        "name": "python",
        "files": ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile"],
        "dirs": [".venv", "venv"],
        "globs": ["*.py"],
        "env": "EDITORS_PYTHON",
        "editors": ["pycharm", "idea", "code"],
    },
    # TypeScript (before JavaScript)
    {
        "name": "typescript",
        "files": ["tsconfig.json"],
        "env": "EDITORS_TYPESCRIPT",
        "editors": ["webstorm", "code"],
    },
    # JavaScript/Node
    {
        "name": "javascript",
        "files": ["package.json"],
        "globs": ["*.js"],
        "env": "EDITORS_JAVASCRIPT",
        "editors": ["webstorm", "phpstorm", "idea", "code"],
    },
    # Go
    {
        "name": "go",
        "files": ["go.mod"],
        "globs": ["*.go"],
        "env": "EDITORS_GO",
        "editors": ["goland", "idea", "code"],
    },
    # Rust
    {
        "name": "rust",
        "files": ["Cargo.toml"],
        "globs": ["*.rs"],
        "env": "EDITORS_RUST",
        "editors": ["rustrover", "idea", "code"],
    },
    # Ruby
    {
        "name": "ruby",
        "files": ["Gemfile"],
        "globs": ["*.rb"],
        "env": "EDITORS_RUBY",
        "editors": ["rubymine", "code"],
    },
    # C/C++
    {
        "name": "cpp",
        "files": ["CMakeLists.txt", "Makefile", "configure.ac", "meson.build"],
        "globs": ["*.c", "*.cpp", "*.h", "*.hpp"],
        "env": "EDITORS_CPP",
        "editors": ["clion", "code"],
    },
]


# Editor definitions (availability checked at runtime in __init__)
EDITOR_DEFS = {
    "code": {"name": "VS Code", "icon": {"path": "images/vscode.svg"}},
    "obsidian": {"name": "Obsidian", "icon": {"path": "images/obsidian.png"}},
    "idea": {"name": "IntelliJ IDEA", "icon": {"path": "images/idea.svg"}},
    "phpstorm": {"name": "PHPStorm", "icon": {"path": "images/phpstorm.svg"}},
    "webstorm": {"name": "WebStorm", "icon": {"path": "images/webstorm.svg"}},
    "pycharm": {"name": "PyCharm", "icon": {"path": "images/pycharm.svg"}},
    "goland": {"name": "GoLand", "icon": {"path": "images/goland.svg"}},
    "rustrover": {"name": "RustRover", "icon": {"path": "images/rustrover.svg"}},
    "rubymine": {"name": "RubyMine", "icon": {"path": "images/rubymine.svg"}},
    "clion": {"name": "CLion", "icon": {"path": "images/clion.svg"}},
}


class Editors:
    def __init__(self):
        self.default_editor = (
            os.environ["DEFAULT_EDITOR"]
            if ("DEFAULT_EDITOR" in os.environ and os.environ["DEFAULT_EDITOR"])
            else "code"
        )
        # Check editor availability in parallel for faster startup
        self.editors = self._check_editors_availability()

    def _check_editors_availability(self) -> dict:
        """Check all editors availability in parallel."""
        from concurrent.futures import ThreadPoolExecutor

        def check_editor(item: tuple) -> tuple:
            code, info = item
            return code, {**info, "available": bool(which(code))}

        with ThreadPoolExecutor(max_workers=len(EDITOR_DEFS)) as executor:
            results = executor.map(check_editor, EDITOR_DEFS.items())

        return dict(results)

    def get_editor(self, editor_code: str) -> dict:
        """Get editor info, dynamically adding unknown editors if available."""
        if editor_code not in self.editors:
            self._register_dynamic_editor(editor_code)
        return self.editors.get(editor_code)

    def _register_dynamic_editor(self, editor_code: str) -> None:
        """Register an editor not in EDITOR_DEFS if it's available on the system."""
        path = which(editor_code)
        if path:
            # Create a display name from the command (e.g., "cursor" -> "Cursor")
            display_name = editor_code.replace("-", " ").replace("_", " ").title()
            self.editors[editor_code] = {
                "name": display_name,
                "available": True,
                "icon": {"path": "icon.png"},  # Use workflow icon as fallback
            }
            logger.debug(f"registered dynamic editor: {editor_code} -> {path}")
        else:
            # Mark as unavailable so we don't check again
            self.editors[editor_code] = {
                "name": editor_code,
                "available": False,
                "icon": {"path": "icon.png"},
            }

    def get_first_available_editor(self, editor_codes: list[str]) -> str:
        """Get the first available editor from the list, including dynamic editors."""
        for editor_code in editor_codes:
            # Check known editors first
            if editor_code in self.editors:
                if self.editors[editor_code]["available"]:
                    return editor_code
            else:
                # Try to register unknown editor dynamically
                self._register_dynamic_editor(editor_code)
                if self.editors[editor_code]["available"]:
                    return editor_code
        return self.default_editor

    def get_editors_from_environment(self, env_var_name, defaults):
        logger.debug(f"getting editors from environment variable {env_var_name}")
        var_names = [env_var_name] if isinstance(env_var_name, str) else (env_var_name or [])
        logger.debug(f"var_names: {var_names}")
        editors = None
        for var_name in var_names:
            if var_name and var_name in os.environ and os.environ[var_name]:
                editors = os.environ[var_name]
                break
        if not editors:
            return defaults
        return [editor.strip() for editor in editors.lower().split(",")]

    def _matches_detector(self, path: str, detector: dict) -> bool:
        """Check if a path matches a detector's rules."""
        # Check exclude conditions first
        if "exclude_dirs" in detector and any(
            os.path.isdir(os.path.join(path, d)) for d in detector["exclude_dirs"]
        ):
            return False

        # Check for matching directories
        if "dirs" in detector and any(
            os.path.isdir(os.path.join(path, d)) for d in detector["dirs"]
        ):
            return True

        # Check for matching files
        if "files" in detector and any(
            os.path.isfile(os.path.join(path, f)) for f in detector["files"]
        ):
            return True

        # Check for matching glob patterns
        return "globs" in detector and any(
            len(glob.glob(os.path.join(path, g))) > 0 for g in detector["globs"]
        )

    def determine_editor(self, path: str) -> str:
        """Determine the appropriate editor for a project path."""
        logger.debug(f"determining editor for {path}")

        for detector in DETECTORS:
            if self._matches_detector(path, detector):
                logger.debug(f"matched detector: {detector['name']}")
                return self.get_first_available_editor(
                    self.get_editors_from_environment(detector.get("env"), detector["editors"])
                )

        return self.default_editor
