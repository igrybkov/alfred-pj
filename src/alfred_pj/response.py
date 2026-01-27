"""Alfred response formatting."""


class ResponseItem:
    def __init__(self, title, subtitle, arg, icon, calls=0, score=0):
        self.title = title
        self.subtitle = subtitle
        self.arg = arg
        self.match = title.lower() + " " + subtitle.lower()
        self.icon = icon
        self.calls = calls
        self.score = score
