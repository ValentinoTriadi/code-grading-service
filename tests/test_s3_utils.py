import pytest

from src.utils.s3 import (
    is_s3_compatible_presigned_url,
    is_s3_presigned_url,
    normalize_object_storage_reference,
    normalize_s3_reference,
    redact_url_query,
)


class TestS3Utils:
    def test_normalize_s3_uri(self):
        result = normalize_object_storage_reference("s3://bucket-a/path/to/code.py")

        assert result == "https://bucket-a.s3.amazonaws.com/path/to/code.py"

    def test_normalize_r2_uri(self):
        result = normalize_object_storage_reference(
            "r2://bucket-a/path/to/code.py",
            r2_account_id="acc123",
        )

        assert result == "https://acc123.r2.cloudflarestorage.com/bucket-a/path/to/code.py"

    def test_normalize_minio_uri(self):
        result = normalize_object_storage_reference(
            "minio://bucket-a/path/to/code.py",
            minio_endpoint="https://minio.local",
        )

        assert result == "https://minio.local/bucket-a/path/to/code.py"

    def test_r2_requires_account_id(self):
        with pytest.raises(ValueError, match="r2:// URL requires r2_account_id"):
            normalize_object_storage_reference("r2://bucket-a/path/code.py")

    def test_minio_requires_endpoint(self):
        with pytest.raises(ValueError, match="minio:// URL requires minio_endpoint"):
            normalize_object_storage_reference("minio://bucket-a/path/code.py")

    def test_presigned_url_detected(self):
        s3_url = (
            "https://bucket-a.s3.amazonaws.com/path/to/code.py"
            "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
            "&X-Amz-Credential=test"
            "&X-Amz-Date=20260226T010101Z"
            "&X-Amz-Expires=3600"
            "&X-Amz-SignedHeaders=host"
            "&X-Amz-Signature=abc123"
        )
        r2_url = (
            "https://acc123.r2.cloudflarestorage.com/bucket-a/path/to/code.py"
            "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
            "&X-Amz-Credential=test"
            "&X-Amz-Date=20260226T010101Z"
            "&X-Amz-Expires=3600"
            "&X-Amz-SignedHeaders=host"
            "&X-Amz-Signature=abc123"
        )
        minio_url = (
            "https://minio.local/bucket-a/path/to/code.py"
            "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
            "&X-Amz-Credential=test"
            "&X-Amz-Date=20260226T010101Z"
            "&X-Amz-Expires=3600"
            "&X-Amz-SignedHeaders=host"
            "&X-Amz-Signature=abc123"
        )

        assert is_s3_compatible_presigned_url(s3_url) is True
        assert is_s3_compatible_presigned_url(r2_url) is True
        assert is_s3_compatible_presigned_url(minio_url) is True

    def test_legacy_alias_kept(self):
        url = (
            "https://bucket-a.s3.amazonaws.com/path/to/code.py"
            "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
            "&X-Amz-Credential=test"
            "&X-Amz-Date=20260226T010101Z"
            "&X-Amz-Expires=3600"
            "&X-Amz-SignedHeaders=host"
            "&X-Amz-Signature=abc123"
        )

        assert is_s3_presigned_url(url) is True
        assert normalize_s3_reference("s3://bucket/path.py") == "https://bucket.s3.amazonaws.com/path.py"

    def test_non_presigned_url_not_detected(self):
        assert is_s3_compatible_presigned_url("https://example.com/code.py") is False

    def test_redact_presigned_query(self):
        url = "https://bucket-a.s3.amazonaws.com/code.py?X-Amz-Signature=abc"

        assert redact_url_query(url) == "https://bucket-a.s3.amazonaws.com/code.py?REDACTED"
