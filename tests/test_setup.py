"""Tests for kattis setup helpers."""

from pathlib import Path
from typing import Any

from unittest.mock import MagicMock

import requests

from kattis_cli.kattis_setup import SetupManager
import kattis_cli.kattis_setup as kattis_setup_module


VALID_KATTISRC = """[user]
username: demo
token: secret

[kattis]
hostname: open.kattis.com
loginurl: https://open.kattis.com/login
submissionurl: https://open.kattis.com/submit
submissionsurl: https://open.kattis.com/submissions
"""


def test_is_valid_kattisrc() -> None:
    """Downloaded kattisrc payload validation should be strict enough."""
    assert SetupManager._is_valid_kattisrc(VALID_KATTISRC)
    assert not SetupManager._is_valid_kattisrc("<html>login page</html>")


def test_download_kattisrc_uses_fallback_headers(monkeypatch: Any) -> None:
    """If first request fails, setup retries with fallback headers."""
    manager = SetupManager(client=MagicMock())
    calls = {'count': 0}

    def fake_get(*args: Any, **kwargs: Any) -> Any:
        response = requests.Response()
        if calls['count'] == 0:
            calls['count'] += 1
            response.status_code = 403
            response._content = b"forbidden"
            return response
        response.status_code = 200
        response._content = VALID_KATTISRC.encode('utf-8')
        return response

    monkeypatch.setattr(kattis_setup_module.requests, 'get', fake_get)
    content = manager._download_kattisrc(requests.cookies.RequestsCookieJar())
    assert content is not None
    assert 'hostname: open.kattis.com' in content


def test_download_kattisrc_uses_session_fallback(monkeypatch: Any) -> None:
    """If cookie download fails, setup retries via authenticated session."""
    manager = SetupManager(client=MagicMock())

    def fake_get(*args: Any, **kwargs: Any) -> Any:
        response = requests.Response()
        response.status_code = 200
        response._content = b"<html>login page</html>"
        return response

    class DummySession:
        def __enter__(self) -> 'DummySession':
            return self

        def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

        def post(self, *args: Any, **kwargs: Any) -> Any:
            response = requests.Response()
            response.status_code = 200
            response._content = b"ok"
            return response

        def get(self, *args: Any, **kwargs: Any) -> Any:
            response = requests.Response()
            response.status_code = 200
            response._content = VALID_KATTISRC.encode('utf-8')
            return response

    monkeypatch.setattr(kattis_setup_module.requests, 'get', fake_get)
    monkeypatch.setattr(kattis_setup_module.requests,
                        'Session', lambda: DummySession())

    content = manager._download_kattisrc(
        requests.cookies.RequestsCookieJar(),
        'demo',
        'secret',
    )
    assert content is not None
    assert 'hostname: open.kattis.com' in content


def test_setup_saves_kattisrc_and_returns(
        monkeypatch: Any, tmp_path: Path) -> None:
    """Successful setup saves the file and exits the loop immediately."""
    mock_client = MagicMock()
    login_response = MagicMock()
    login_response.status_code = 200
    login_response.cookies = requests.cookies.RequestsCookieJar()
    mock_client.login.return_value = login_response

    manager = SetupManager(client=mock_client)
    monkeypatch.setattr(manager, 'check_kattisrc', lambda: False)
    monkeypatch.setattr(manager, '_download_kattisrc',
                        lambda cookies, username='', password='':
                        VALID_KATTISRC)
    monkeypatch.setattr(kattis_setup_module, '_KATTISRC',
                        tmp_path / '.kattisrc')

    confirm_answers = iter([True, False])

    def fake_confirm(*args: Any, **kwargs: Any) -> bool:
        return next(confirm_answers)

    monkeypatch.setattr(kattis_setup_module.Confirm, 'ask', fake_confirm)
    monkeypatch.setattr(kattis_setup_module.Prompt, 'ask',
                        lambda *args, **kwargs: 'demo')

    manager.setup()

    saved = tmp_path / '.kattisrc'
    assert saved.exists()
    assert 'username: demo' in saved.read_text(encoding='utf-8')
    assert mock_client.login.call_count == 1
