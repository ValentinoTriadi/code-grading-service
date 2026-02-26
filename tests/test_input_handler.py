from src.engine.input_handler import InputHandler


class TestInputHandler:
    """Tests for InputHandler."""

    def test_placeholder(self):
        handler = InputHandler()
        assert handler is not None
