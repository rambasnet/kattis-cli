"""Test the Unitlity module.
"""


import shutil
from pathlib import Path
from kattis_cli.utils import utility, config


def test_guess_mainfile() -> None:
    """Test utility.guess_mainfile function."""
    if not Path.home().joinpath('.kattis-cli.toml').exists():
        shutil.copyfile(
            './kattis_cli/.kattis-cli.toml',
            Path.home().joinpath('.kattis-cli.toml'))
    lang_config = config.parse_config('python3')
    main_file = utility.guess_mainfile('python3', [], 'cold', lang_config)
    assert main_file == 'cold.py'
    main_file = utility.guess_mainfile(
        'python3', ['cold.py'], 'cold', lang_config)
    assert main_file == 'cold.py'
    main_file = utility.guess_mainfile(
        'python3', ['cold.py', 'cold2.py', 'main.py'], 'cold', lang_config)
    assert main_file == 'cold.py'
    main_file = utility.guess_mainfile(
        'python3',
        ['cold2.py',
         'cold.py', 'test_cold.py'], 'cold', lang_config)
    assert main_file == 'cold.py'


def test_valididate_language_true() -> None:
    """
    Test utility.validate_language
    """
    assert utility.validate_language('python3') is True


def test_valididate_language_false() -> None:
    """
    Test utility.validate_language
    """
    try:
        utility.validate_language('d++')
    except SystemExit:
        assert True
