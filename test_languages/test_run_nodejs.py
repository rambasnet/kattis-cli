""" Test run_program.py for Nodejs Solutions.
"""

from pathlib import Path
import shutil
from kattis_cli.utils import run_program, config


def test_run_nodejs_success() -> None:
    """Test run_program.py for Python programs
    """
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './src/kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    root_folder = Path('tests/cold')
    main_program = str(root_folder.joinpath('nodejs').joinpath('cold.js'))
    lang_config = config.parse_config('nodejs')
    for file in root_folder.joinpath('data').glob('*.in'):
        input_file = str(file)
        code, ans, _ = run_program.run(
            lang_config, main_program, input_file)
        output = file.with_suffix('.ans').read_text(encoding='utf-8')
        # print(ans)
        # print(output)
        assert code == 0
        assert ans == output


def test_run_nodejs_fail() -> None:
    """Test run_program.py for Python programs
    """
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './src/kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    root_folder = Path('tests/cold')
    main_program = str(root_folder.joinpath(
        'nodejs').joinpath('cold_error.js'))
    lang_config = config.parse_config('nodejs')
    code, output, error = run_program.compile_program(
        lang_config, [main_program])
    # print(code, output, error)
    assert code != 0
    assert output == ''
    assert error != ''
