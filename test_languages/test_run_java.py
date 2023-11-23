""" Test run_program.py for Java Solutions.
"""

from pathlib import Path
import shutil
import os
from kattis_cli.utils import run_program, config, utility


def test_run_java_success() -> None:
    """Test run_program.py for Java programs
    """
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    root_folder = Path('tests/cold')
    main_program = str(root_folder.joinpath('java').joinpath('Cold.java'))
    lang_config = config.parse_config('java')
    code, ans, _ = run_program.compile_program(lang_config, [main_program])
    assert code == 0
    main_class = utility.guess_mainfile(
        'java', [main_program], 'cold', lang_config)
    # main_class = "Cold"
    # print(f'{main_class=}')
    for file in root_folder.joinpath('data').glob('*.in'):
        input_file = str(file)
        code, ans, error = run_program.run(lang_config, main_class, input_file)
        output = file.with_suffix('.ans').read_text(encoding='utf-8')
        # print(f'{code=}, {ans=}, {error=}')
        assert code == 0
        assert ans == output
        assert error == ''
    os.remove('Cold.class')


def test_run_java_fail() -> None:
    """Test run_program.py for Java programs; fail
    """
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    root_folder = Path('tests/cold')
    main_program = str(root_folder.joinpath(
        'java').joinpath('Cold_error.java'))
    lang_config = config.parse_config('java')
    code, output, error = run_program.compile_program(
        lang_config, [main_program])
    # print(f'{code=}, {output=}, {error=}')
    assert code == 1
    assert output == ''
    assert error != ''
