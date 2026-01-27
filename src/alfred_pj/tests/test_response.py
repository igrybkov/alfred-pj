"""Tests for Alfred response formatting."""

from alfred_pj.response import ResponseItem


class TestResponseItem:
    """Tests for ResponseItem class."""

    def test_basic_creation(self):
        """Should create ResponseItem with all fields."""
        item = ResponseItem(
            title="My Project",
            subtitle="Open in VS Code",
            arg="/path/to/project",
            icon={"path": "images/vscode.svg"},
        )

        assert item.title == "My Project"
        assert item.subtitle == "Open in VS Code"
        assert item.arg == "/path/to/project"
        assert item.icon == {"path": "images/vscode.svg"}

    def test_match_field_combines_title_and_subtitle(self):
        """Match field should be lowercase title + subtitle."""
        item = ResponseItem(
            title="MyProject",
            subtitle="Open in Editor",
            arg="/path",
            icon={},
        )

        assert item.match == "myproject open in editor"

    def test_match_field_is_lowercase(self):
        """Match field should be all lowercase."""
        item = ResponseItem(
            title="UPPERCASE Project",
            subtitle="SUBTITLE HERE",
            arg="/path",
            icon={},
        )

        assert item.match == "uppercase project subtitle here"

    def test_default_calls(self):
        """Calls should default to 0."""
        item = ResponseItem(
            title="Test",
            subtitle="Test",
            arg="/path",
            icon={},
        )

        assert item.calls == 0

    def test_default_score(self):
        """Score should default to 0."""
        item = ResponseItem(
            title="Test",
            subtitle="Test",
            arg="/path",
            icon={},
        )

        assert item.score == 0

    def test_custom_calls(self):
        """Should accept custom calls count."""
        item = ResponseItem(
            title="Test",
            subtitle="Test",
            arg="/path",
            icon={},
            calls=42,
        )

        assert item.calls == 42

    def test_custom_score(self):
        """Should accept custom score."""
        item = ResponseItem(
            title="Test",
            subtitle="Test",
            arg="/path",
            icon={},
            score=100,
        )

        assert item.score == 100

    def test_serializable_to_dict(self):
        """Should have __dict__ for JSON serialization."""
        item = ResponseItem(
            title="Project",
            subtitle="Subtitle",
            arg="/path",
            icon={"path": "icon.png"},
            calls=5,
            score=10,
        )

        d = item.__dict__
        assert d["title"] == "Project"
        assert d["subtitle"] == "Subtitle"
        assert d["arg"] == "/path"
        assert d["icon"] == {"path": "icon.png"}
        assert d["match"] == "project subtitle"
        assert d["calls"] == 5
        assert d["score"] == 10
