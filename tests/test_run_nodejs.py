""" Test run_program.py for Nodejs Solutions.
"""

from pathlib import Path
from kattis_cli.utils import run_program


def test_run_python_success() -> None:
    """Test run_program.py for Python programs
    """
    root_folder = Path('tests/cold')
    main_program = str(root_folder.joinpath('nodejs').joinpath('cold.js'))
    for file in root_folder.joinpath('data').glob('*.in'):
        input_file = str(file)
        code, ans, _ = run_program.run('node.js', main_program, input_file)
        output = file.with_suffix('.ans').read_text(encoding='utf-8')
        # print(ans)
        # print(output)
        assert code == 0
        assert ans == output


def test_run_python_fail() -> None:
    """Test run_program.py for Python programs
    """
    root_folder = Path('tests/cold')
    main_program = str(root_folder.joinpath('nodejs').joinpath('cold_error.js'))
    for file in root_folder.joinpath('data').glob('*.in'):
        input_file = str(file)
        code, ans, error = run_program.run('Javascript (Node.js)', main_program, input_file)
        output = file.with_suffix('.ans').read_text(encoding='utf-8')
        # print(ans)
        # print(output)
        assert code != 0
        assert ans != output
        assert error != ''
