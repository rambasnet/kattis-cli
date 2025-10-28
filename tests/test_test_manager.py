"""Unit tests for TestManager.

These tests exercise the sample-run flow using temporary files and
monkeypatching to avoid network or real compilation steps.
"""

from pathlib import Path
from typing import Any

import pytest

from kattis_cli.solution_tester import SolutionTester
from kattis_cli import kattis as kattis_module
from kattis_cli.utils import run_program, utility
from rich.prompt import Confirm


def _write_sample(
    tmp_path: Path,
    problem_root: str,
    in_content: str,
    ans_content: str,
    in_name: str = "sample1.in",
) -> str:
    """Create a temporary problem folder with a data / directory.

    Returns the problem root path as a string.
    """
    root = tmp_path / problem_root
    data = root / "data"
    data.mkdir(parents=True)
    in_file = data / in_name
    ans_file = data / in_name.replace('.in', '.ans')
    in_file.write_text(in_content)
    ans_file.write_text(ans_content)
    return str(root)


def test_testmanager_all_pass_triggers_submit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """When samples pass, the user is prompted and submit_solution is
    called when they confirm.
    """
    problemid = "prob"
    loc_language = "python"
    mainclass = "main.py"
    problem_root = _write_sample(tmp_path, "prob", "input\n", "output\n")
    files = ["main.py"]
    lang_config = {"compile": False}

    def fake_run(lc: Any, mc: Any, infile: str) -> tuple:
        return (0, "output\n", "")

    monkeypatch.setattr(run_program, "run", fake_run)

    def fake_check(expected: str, ans: str, accuracy: Any) -> bool:
        return expected.strip() == ans.strip()

    monkeypatch.setattr(utility, "check_answer", fake_check)

    called: dict = {}

    def fake_submit(
        files_arg: list,
        problemid_arg: str,
        kat_lang: str,
        mainclass_arg: str,
        tag: str = "",
        force: bool = False,
    ) -> None:
        called["args"] = (
            files_arg,
            problemid_arg,
            kat_lang,
            mainclass_arg,
            tag,
            force,
        )

    monkeypatch.setattr(kattis_module, "submit_solution", fake_submit)
    monkeypatch.setattr(Confirm, "ask", lambda prompt,
                        default=True: True)  # type: ignore

    tm = SolutionTester(client=kattis_module)

    tm.test_samples(problemid, loc_language, mainclass,
                    problem_root, files, lang_config)

    assert "args" in called
    assert called["args"][1] == problemid


def test_testmanager_failure_no_submit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """When a sample fails, Confirm.ask should not be invoked and no
    submission should be attempted.
    """
    problemid = "prob"
    loc_language = "python"
    mainclass = "main.py"
    problem_root = _write_sample(tmp_path, "prob", "input\n", "different\n")
    files = ["main.py"]
    lang_config = {"compile": False}

    def fake_run(lc: Any, mc: Any, infile: str) -> tuple:
        return (0, "output\n", "")

    monkeypatch.setattr(run_program, "run", fake_run)

    monkeypatch.setattr(utility, "check_answer",
                        lambda expected, ans, accuracy: False)

    called: dict = {}

    def fake_submit(*args: Any, **kwargs: Any) -> None:
        called["called"] = True

    monkeypatch.setattr(kattis_module, "submit_solution", fake_submit)

    def fail_confirm(prompt: str, default: bool = True) -> bool:
        pytest.fail("Confirm.ask should not be called on failures")

    monkeypatch.setattr(Confirm, "ask", fail_confirm)  # type: ignore

    tm = SolutionTester(client=kattis_module)

    tm.test_samples(problemid, loc_language, mainclass,
                    problem_root, files, lang_config)

    assert "called" not in called
