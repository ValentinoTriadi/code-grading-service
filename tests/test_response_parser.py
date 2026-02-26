from src.engine.response_parser import ResponseParser


class TestResponseParser:
    """Tests for ResponseParser."""

    def test_placeholder(self):
        parser = ResponseParser()
        assert parser is not None
