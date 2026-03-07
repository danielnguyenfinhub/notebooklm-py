"""Network security utilities for trusted URL validation.

Validates dynamic upload/download URLs to ensure credentials are only sent
to trusted Google hosts. Used by _sources.py (resumable upload) and
_artifacts.py (artifact downloads).
"""

import ipaddress
import os
from urllib.parse import urlparse

from .exceptions import ValidationError

# Default trusted hostname suffixes (leading dot for subdomain matching)
DEFAULT_TRUSTED_SUFFIXES = (".google.com", ".googleusercontent.com", ".googleapis.com")

_ENV_TRUSTED_UPLOAD_HOSTS = "NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS"


def parse_trusted_extra_hosts_from_env() -> tuple[str, ...]:
    """Parse comma-separated extra trusted hostnames from environment.

    Reads NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS. Values are stripped and empty
    entries ignored. Hostnames are returned in lowercase.

    Returns:
        Tuple of extra hostnames (exact match only, no wildcards).
    """
    raw = os.environ.get(_ENV_TRUSTED_UPLOAD_HOSTS, "").strip()
    if not raw:
        return ()
    hosts = [h.strip().lower() for h in raw.split(",") if h.strip()]
    return tuple(hosts)


def validate_trusted_https_url(
    url: str,
    *,
    purpose: str,
    extra_hosts: tuple[str, ...] | None = None,
) -> None:
    """Validate that a URL is HTTPS and its host is trusted before sending credentials.

    - Requires https scheme.
    - Requires a hostname (rejects IP literals).
    - Rejects embedded username/password.
    - Rejects explicit non-443 ports.
    - Allows hosts whose name ends with DEFAULT_TRUSTED_SUFFIXES or is in extra_hosts.

    Args:
        url: The URL to validate.
        purpose: Short description for error messages (e.g. "resumable upload start").
        extra_hosts: Optional tuple of exact hostnames from env override.

    Raises:
        ValidationError: If the URL is not trusted, with an actionable message
            that includes upgrade hint and NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS.
    """
    parsed = urlparse(url)
    if not parsed.scheme:
        raise ValidationError(
            f"Invalid URL for {purpose}: missing scheme. "
            "Use https only. If you need a new host allowed, set NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS "
            "or upgrade notebooklm-py."
        )
    if parsed.scheme != "https":
        raise ValidationError(
            f"URL for {purpose} must use HTTPS (got {parsed.scheme}). "
            "If you need a new host allowed, set NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS "
            "or upgrade notebooklm-py."
        )
    host = (parsed.hostname or "").strip().lower()
    if not host:
        raise ValidationError(
            f"Invalid URL for {purpose}: missing hostname. "
            "If you need a new host allowed, set NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS "
            "or upgrade notebooklm-py."
        )
    if parsed.username is not None or parsed.password is not None:
        raise ValidationError(
            f"URL for {purpose} must not contain username/password. "
            "If you need a new host allowed, set NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS "
            "or upgrade notebooklm-py."
        )
    if parsed.port is not None and parsed.port != 443:
        raise ValidationError(
            f"URL for {purpose} must use default HTTPS port 443 (got port {parsed.port}). "
            "If you need a new host allowed, set NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS "
            "or upgrade notebooklm-py."
        )
    try:
        ipaddress.ip_address(host)
        raise ValidationError(
            f"URL for {purpose} must use a hostname, not an IP address. "
            "If you need a new host allowed, set NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS "
            "or upgrade notebooklm-py."
        )
    except ValueError:
        pass  # Not an IP, which is what we want

    extra = extra_hosts if extra_hosts is not None else parse_trusted_extra_hosts_from_env()
    if host in extra:
        return
    for suffix in DEFAULT_TRUSTED_SUFFIXES:
        if host == suffix.lstrip(".") or host.endswith(suffix):
            return
    raise ValidationError(
        f"Untrusted host for {purpose}: {host}. "
        "Allowed: *.google.com, *.googleusercontent.com, *.googleapis.com, or set "
        "NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS for exact hostnames. Upgrade notebooklm-py if a "
        "legitimate Google host is rejected."
    )


def redact_url_for_logs(url: str) -> str:
    """Redact URL for safe logging (scheme + host only, no path/query)."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").strip().lower()
    if not host:
        return "<invalid-url>"
    return f"{parsed.scheme or 'https'}://{host}/..."
