from src.api.controllers.grading import GradingController


class TestGradingController:
    def test_supports_normal_zip_file_entry(self):
        assert GradingController._is_supported_zip_entry("student1.py") is True

    def test_rejects_directory_entries(self):
        assert GradingController._is_supported_zip_entry("submissions/") is False

    def test_rejects_macosx_entries(self):
        assert (
            GradingController._is_supported_zip_entry("__MACOSX/student1.py") is False
        )
        assert (
            GradingController._is_supported_zip_entry("folder/__MACOSX/meta.txt")
            is False
        )
