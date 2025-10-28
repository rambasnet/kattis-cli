"""Compatibility thin wrapper exposing a KattisClient instance.

Refactored: main functionality moved to `kattis_cli.client.KattisClient`.
This module keeps the original functional API by delegating to a
module-level client instance so existing call-sites do not need to change.
"""

from typing import Any, List
from kattis_cli.client import KattisClient

# Single client used by module-level functions for backward compatibility
_client = KattisClient()


def login(login_url: str, username: str, password: str = '', token: str = '') -> Any:
    return _client.login(login_url, username, password, token)


def login_from_config(cfg: Any) -> Any:
    return _client.login_from_config(cfg)


def submit(submit_url: str, cookies: Any, problem: str,
           language: str, files: List[str], mainclass: str, tag: str) -> Any:
    return _client.submit(submit_url, cookies, problem, language, files, mainclass, tag)


def get_submission_status(submission_url: str, cookies: Any) -> Any:
    return _client.get_submission_status(submission_url, cookies)


def get_submission_url(submit_response: str, cfg: Any) -> str:
    return _client.get_submission_url(submit_response, cfg)


def parse_row_html(html: str) -> Any:
    return _client.parse_row_html(html)


def show_kattis_judgement(problemid: str, submission_url: str, cfg: Any) -> None:
    return _client.show_kattis_judgement(problemid, submission_url, cfg)


def get_login_reply(cfg: Any) -> Any:
    return _client.get_login_reply(cfg)


def submit_solution(files: List[str], problemid: str, language: str,
                    mainclass: str, tag: str, force: bool) -> None:
    return _client.submit_solution(files, problemid, language, mainclass, tag, force)
