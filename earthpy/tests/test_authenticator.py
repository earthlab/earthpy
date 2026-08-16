import pytest
from unittest.mock import patch

from ..api.auth import Authenticator


@pytest.fixture
def earthdata_auth():
    # Only use env and netrc backends (no keyring)
    return Authenticator("earthdata", priority=["netrc", "env"])


def test_missing_credentials_noninteractive(monkeypatch, earthdata_auth):
    # Ensure env and netrc don't interfere
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)

    with pytest.raises(RuntimeError, match="No credentials found"):
        earthdata_auth.get_credentials(interactive=False)


def test_env_credentials(monkeypatch, earthdata_auth):
    monkeypatch.setenv("EARTHDATA_USERNAME", "env_user")
    monkeypatch.setenv("EARTHDATA_PASSWORD", "env_pass")

    username, password = earthdata_auth.get_credentials(interactive=False)

    assert username == "env_user"
    assert password == "env_pass"


def test_prompt_for_credentials(monkeypatch, earthdata_auth):
    """Test that users are prompted for credentials when interactive."""
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)

    with patch("builtins.input", return_value="prompt_user"), patch(
        "getpass.getpass", return_value="prompt_pass"
    ):
        username, password = earthdata_auth.get_credentials(interactive=True)

    assert username == "prompt_user"
    assert password == "prompt_pass"


def test_env_priority(monkeypatch, earthdata_auth):
    """Test that env variables are checked with netrc priority."""
    monkeypatch.setenv("EARTHDATA_USERNAME", "env_user")
    monkeypatch.setenv("EARTHDATA_PASSWORD", "env_pass")

    username, password = earthdata_auth.get_credentials(interactive=False)

    assert username == "env_user"
    assert password == "env_pass"
