"""Unit tests for _netsec trusted URL validation."""

import pytest

from notebooklm._netsec import (
    DEFAULT_TRUSTED_SUFFIXES,
    parse_trusted_extra_hosts_from_env,
    redact_url_for_logs,
    validate_trusted_https_url,
)
from notebooklm.exceptions import ValidationError


class TestValidateTrustedHttpsUrl:
    """Tests for validate_trusted_https_url."""

    def test_https_required(self):
        """HTTP URLs are rejected."""
        with pytest.raises(ValidationError, match="must use HTTPS"):
            validate_trusted_https_url("http://content.googleapis.com/file", purpose="test")

    def test_hostname_required(self):
        """URLs without hostname are rejected."""
        with pytest.raises(ValidationError, match="missing hostname"):
            validate_trusted_https_url("https:///path", purpose="test")

    def test_ip_literal_rejected(self):
        """IP literals are rejected."""
        with pytest.raises(ValidationError, match="hostname, not an IP"):
            validate_trusted_https_url("https://192.168.1.1/file", purpose="test")
        with pytest.raises(ValidationError, match="hostname, not an IP"):
            validate_trusted_https_url("https://[::1]/file", purpose="test")

    def test_userinfo_rejected(self):
        """Embedded username/password are rejected."""
        with pytest.raises(ValidationError, match="must not contain username"):
            validate_trusted_https_url(
                "https://user:pass@content.googleapis.com/file", purpose="test"
            )

    def test_non_443_port_rejected(self):
        """Explicit non-443 ports are rejected."""
        with pytest.raises(ValidationError, match="port 443"):
            validate_trusted_https_url("https://content.googleapis.com:8443/file", purpose="test")

    def test_trusted_google_hosts_accepted(self):
        """Trusted Google suffixes are accepted."""
        validate_trusted_https_url("https://notebooklm.google.com/", purpose="test")
        validate_trusted_https_url(
            "https://upload.googleusercontent.com/session123", purpose="test"
        )
        validate_trusted_https_url("https://content.googleapis.com/upload/session", purpose="test")
        validate_trusted_https_url("https://subdomain.google.com/path", purpose="test")

    def test_evil_host_rejected(self):
        """Untrusted hosts are rejected."""
        with pytest.raises(ValidationError, match="Untrusted host"):
            validate_trusted_https_url("https://evil.example.com/session", purpose="test")
        with pytest.raises(ValidationError, match="Untrusted host"):
            validate_trusted_https_url("https://upload.example.com/session", purpose="test")

    def test_override_host_accepted(self, monkeypatch):
        """NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS override is accepted."""
        monkeypatch.setenv("NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS", "upload.example.com")
        validate_trusted_https_url("https://upload.example.com/session123", purpose="test")

    def test_override_multiple_hosts(self, monkeypatch):
        """Comma-separated override hosts work."""
        monkeypatch.setenv(
            "NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS",
            "custom1.example.com, custom2.example.com",
        )
        validate_trusted_https_url("https://custom1.example.com/path", purpose="test")
        validate_trusted_https_url("https://custom2.example.com/path", purpose="test")

    def test_extra_hosts_param(self):
        """extra_hosts parameter overrides env for that call."""
        validate_trusted_https_url(
            "https://allowed.local/host",
            purpose="test",
            extra_hosts=("allowed.local",),
        )
        with pytest.raises(ValidationError, match="Untrusted host"):
            validate_trusted_https_url("https://allowed.local/host", purpose="test")

    def test_error_message_includes_upgrade_and_env(self):
        """Error message mentions upgrade and env var."""
        with pytest.raises(ValidationError) as exc_info:
            validate_trusted_https_url("https://evil.com/x", purpose="test")
        msg = str(exc_info.value)
        assert "NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS" in msg
        assert "upgrade" in msg.lower()


class TestParseTrustedExtraHostsFromEnv:
    """Tests for parse_trusted_extra_hosts_from_env."""

    def test_empty_unset(self, monkeypatch):
        """Unset or empty env returns empty tuple."""
        monkeypatch.delenv("NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS", raising=False)
        assert parse_trusted_extra_hosts_from_env() == ()
        monkeypatch.setenv("NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS", "")
        assert parse_trusted_extra_hosts_from_env() == ()

    def test_single_host(self, monkeypatch):
        """Single host is returned lowercased."""
        monkeypatch.setenv("NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS", "Upload.Example.COM")
        assert parse_trusted_extra_hosts_from_env() == ("upload.example.com",)

    def test_multiple_stripped(self, monkeypatch):
        """Multiple hosts are stripped and lowercased."""
        monkeypatch.setenv("NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS", " a.com , b.com ")
        assert parse_trusted_extra_hosts_from_env() == ("a.com", "b.com")


class TestRedactUrlForLogs:
    """Tests for redact_url_for_logs."""

    def test_redacts_to_scheme_and_host(self):
        """Path and query are redacted."""
        assert (
            redact_url_for_logs("https://content.googleapis.com/upload/session?foo=bar")
            == "https://content.googleapis.com/..."
        )

    def test_invalid_url(self):
        """Invalid URL returns placeholder."""
        assert redact_url_for_logs("") == "<invalid-url>"


class TestDefaultTrustedSuffixes:
    """Sanity check for default suffixes."""

    def test_suffixes_defined(self):
        """Default suffixes match spec."""
        assert ".google.com" in DEFAULT_TRUSTED_SUFFIXES
        assert ".googleusercontent.com" in DEFAULT_TRUSTED_SUFFIXES
        assert ".googleapis.com" in DEFAULT_TRUSTED_SUFFIXES
