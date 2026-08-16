import json

import keyring
import pytest
from unittest.mock import patch, MagicMock

from ..api.auth import Authenticator

@pytest.fixture
def earthdata_auth():
    return Authenticator("earthdata", priority=["keyring", "env"])


def test_missing_credentials_noninteractive(monkeypatch, earthdata_auth):
    # Ensure env doesn't interfere
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)
    try:
        keyring.delete_password("earthdata", "default")
    except:
        pass    

    with pytest.raises(RuntimeError, match="No credentials found"):
        earthdata_auth.get_credentials(interactive=False)
        
def test_env_credentials(monkeypatch, earthdata_auth):
    monkeypatch.setenv("EARTHDATA_USERNAME", "env_user")
    monkeypatch.setenv("EARTHDATA_PASSWORD", "env_pass")

    username, password = earthdata_auth.get_credentials(interactive=False)

    assert username == "env_user"
    assert password == "env_pass"


def test_keyring_credentials(monkeypatch, earthdata_auth):
    # Ensure env doesn't interfere
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)

    creds = json.dumps({"username": "key_user", "password": "key_pass"})
    keyring.set_password("earthdata", "default", creds)

    username, password = earthdata_auth.get_credentials(interactive=False)

    assert username == "key_user"
    assert password == "key_pass"


import tempfile

def test_prompt_and_store(monkeypatch, earthdata_auth):
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)
    try:
        keyring.delete_password("earthdata", "default")
    except keyring.errors.PasswordDeleteError:
        pass

    with patch("builtins.input", return_value="prompt_user"), \
            patch("getpass.getpass", return_value="prompt_pass"):
        username, password = earthdata_auth.get_credentials(
            interactive=True)

    creds = json.loads(keyring.get_password("earthdata", "default"))
    assert creds["username"] == "prompt_user"
    assert creds["password"] == "prompt_pass"


def test_override_existing(monkeypatch, earthdata_auth):
    # Set initial keyring creds
    initial = json.dumps({"username": "old_user", "password": "old_pass"})
    keyring.set_password("earthdata", "default", initial)

    with patch("builtins.input", side_effect=["y", "new_user"]), \
         patch("getpass.getpass", return_value="new_pass"):
        username, password = earthdata_auth.get_credentials(
            interactive=True, override=True)

    # Should have overridden keyring credentials
    creds = json.loads(keyring.get_password("earthdata", "default"))
    assert creds["username"] == "new_user"
    assert creds["password"] == "new_pass"
    assert username == "new_user"
    assert password == "new_pass"


def test_no_override(monkeypatch, earthdata_auth):
    keyring.set_password("earthdata", "default", json.dumps({
        "username": "keep_user",
        "password": "keep_pass"
    }))

    # simulate "no" to override
    with patch("builtins.input", return_value="n"):  
        username, password = earthdata_auth.get_credentials(
            interactive=True, override=True)

    assert username == "keep_user"
    assert password == "keep_pass"
