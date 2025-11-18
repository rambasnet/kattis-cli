""" Test cases for language utility functions. """

import shutil
from pathlib import Path
from kattis_cli.utils import languages, config


def test_guess_mainfile() -> None:
    """Test utility.guess_mainfile function."""
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    lang_config = config.parse_config('python3')
    main_file = languages.guess_mainfile('python3', [], 'cold', lang_config)
    assert main_file == 'cold.py'
    main_file = languages.guess_mainfile(
        'python3', ['cold.py'], 'cold', lang_config)
    assert main_file == 'cold.py'
    main_file = languages.guess_mainfile(
        'python3', ['cold.py', 'cold2.py', 'main.py'], 'cold', lang_config)
    assert main_file == 'cold.py'
    main_file = languages.guess_mainfile(
        'python3',
        ['cold2.py',
         'cold.py', 'test_cold.py'], 'cold', lang_config)
    assert main_file == 'cold.py'


def test_valididate_language_true() -> None:
    """
    Test utility.validate_language
    """
    assert languages.validate_language('python3') is True


def test_valididate_language_false() -> None:
    """
    Test utility.validate_language
    """
    try:
        languages.validate_language('d++')
    except SystemExit:
        assert True


def test_get_coding_files() -> None:
    """Test utility.get_coding_files function."""
    cur_path = Path.cwd() / Path('tests/cold/C++/src')
    print("Path=", str(cur_path))
    files = languages.get_coding_files(cur_path)

    assert len(files) == 3
    assert any(f.endswith('cold.cpp') for f in files)
    assert any(f.endswith('util.cpp') for f in files)
    assert any(f.endswith('util.h') for f in files)


def test_get_coding_files1() -> None:
    """Test utility.get_coding_files function."""
    cur_path = Path.cwd() / Path('tests/cold/C++')
    print("Path=", str(cur_path))
    files = languages.get_coding_files(cur_path)
    assert len(files) == 3
    assert any(f.endswith('cold.cpp') for f in files)
    assert any(f.endswith('util.cpp') for f in files)
    assert any(f.endswith('util.h') for f in files)
