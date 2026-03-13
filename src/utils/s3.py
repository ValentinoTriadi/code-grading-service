from urllib.parse import parse_qs, quote, urlsplit, urlunsplit


def is_s3_compatible_presigned_url(url: str) -> bool:
    """Return True when URL looks like an S3-compatible pre-signed URL.

    Works with AWS S3, Cloudflare R2, MinIO, and other S3-compatible object
    storage services that use AWS signing query parameters.
    """
    parsed = urlsplit(url)
    query = parse_qs(parsed.query)

    if parsed.scheme not in {"http", "https"}:
        return False

    has_v4_keys = (
        "X-Amz-Algorithm" in query
        and "X-Amz-Credential" in query
        and "X-Amz-Signature" in query
        and "X-Amz-Expires" in query
    )
    has_legacy_keys = "AWSAccessKeyId" in query and "Signature" in query

    return has_v4_keys or has_legacy_keys


def normalize_object_storage_reference(
    raw_url: str,
    r2_account_id: str | None = None,
    minio_endpoint: str | None = None,
) -> str:
    """Normalize supported object storage references to fetchable URL.

    Supported:
    - https://... (including pre-signed URLs from S3-compatible providers)
    - http://...
    - s3://bucket/key -> https://bucket.s3.amazonaws.com/key
    - r2://bucket/key -> https://<account_id>.r2.cloudflarestorage.com/bucket/key
    - minio://bucket/key -> <minio_endpoint>/bucket/key
    """
    raw_url = raw_url.strip()

    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        return raw_url

    if raw_url.startswith("s3://"):
        bucket, key = _extract_bucket_key(raw_url, scheme="s3")

        encoded_key = quote(key)
        return f"https://{bucket}.s3.amazonaws.com/{encoded_key}"

    if raw_url.startswith("r2://"):
        bucket, key = _extract_bucket_key(raw_url, scheme="r2")
        if not r2_account_id:
            raise ValueError(
                "r2:// URL requires r2_account_id. Pass it or use a pre-signed https URL"
            )

        encoded_key = quote(key)
        return f"https://{r2_account_id}.r2.cloudflarestorage.com/{bucket}/{encoded_key}"

    if raw_url.startswith("minio://"):
        bucket, key = _extract_bucket_key(raw_url, scheme="minio")
        if not minio_endpoint:
            raise ValueError(
                "minio:// URL requires minio_endpoint. Pass it or use a pre-signed https URL"
            )

        endpoint = minio_endpoint.rstrip("/")
        encoded_key = quote(key)
        return f"{endpoint}/{bucket}/{encoded_key}"

    raise ValueError("Unsupported URL scheme. Use https://, s3://, r2://, or minio://")


def _extract_bucket_key(raw_url: str, scheme: str) -> tuple[str, str]:
    path = raw_url[len(f"{scheme}://") :]
    if "/" not in path:
        raise ValueError(f"Invalid {scheme} URL. Expected format: {scheme}://bucket/key")

    bucket, key = path.split("/", 1)
    if not bucket or not key:
        raise ValueError(f"Invalid {scheme} URL. Expected format: {scheme}://bucket/key")

    return bucket, key


def redact_url_query(url: str) -> str:
    """Redact query parameters for safe logging of signed URLs."""
    parsed = urlsplit(url)
    if not parsed.query:
        return url

    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "REDACTED", parsed.fragment))


def is_s3_presigned_url(url: str) -> bool:
    """Backward-compatible alias for legacy S3 utility name."""
    return is_s3_compatible_presigned_url(url)


def normalize_s3_reference(raw_url: str) -> str:
    """Backward-compatible alias for legacy S3 utility name."""
    return normalize_object_storage_reference(raw_url)


def redact_presigned_url(url: str) -> str:
    """Backward-compatible alias for legacy S3 utility name."""
    return redact_url_query(url)
