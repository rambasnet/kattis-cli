""" Test run_program.py
"""

from pathlib import Path
import os
import shutil
from kattis_cli.utils import run_program, config
from kattis_cli.utils import languages


def test_run_python() -> None:
    """Test run_program.py for Python programs
    """
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './src/kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    root_folder = Path('tests/cold')
    main_program = str(root_folder.joinpath('python3').joinpath('cold.py'))
    lang_config = config.parse_config('python3')
    for file in root_folder.joinpath('data').glob('*.in'):
        input_file = str(file)
        code, ans, _ = run_program.run(lang_config, main_program, input_file)
        output = file.with_suffix('.ans').read_text(encoding='utf-8')
        # print(ans)
        # print(output)
        assert code == 0
        assert ans == output


def test_run_python_no_ans_file() -> None:
    """Test run_program.py for Python programs
    """
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './src/kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    root_folder = Path('tests/OOP')
    main_program = str(root_folder.joinpath('python3').joinpath('cold.py'))
    lang_config = config.parse_config('python3')
    for file in root_folder.joinpath('data').glob('*.in'):
        input_file = str(file)
        code, ans, _ = run_program.run(lang_config, main_program, input_file)
        try:
            output = file.with_suffix('.ans').read_text(encoding='utf-8')
        except FileNotFoundError:
            output = None
            assert code != 0
            assert "No .ans or .out file found!" in ans
        else:
            assert code == 0
            assert ans == output


def test_run_cpp() -> None:
    """Test run_program.py for C++ programs
    """
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './src/kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    cpp_folder = Path('tests/cold/C++')

    files = languages.get_coding_files(cpp_folder)
    lang_config = config.parse_config('cpp')
    main_program = languages.guess_mainfile(
        'cpp', files, 'cold', lang_config)
    code, output, _ = run_program.compile_program(
        lang_config, files)
    assert code == 0
    assert main_program == 'cold.cpp'
    for file in cpp_folder.joinpath('data').glob('*.in'):
        input_file = str(file)
        code, ans, _ = run_program.run(lang_config, main_program, input_file)
        output = file.with_suffix('.ans').read_text(encoding='utf-8')
        # print(ans)
        # print(output)
        assert code == 0
        assert ans == output
    os.remove('a.out')
