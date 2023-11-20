"""Test the Unitlity module.
"""


from kattis_cli.utils import utility


def test_guess_mainfile() -> None:
    """Test utility.guess_mainfile function."""
    main_file = utility.guess_mainfile('Python 3', [], 'cold')
    assert main_file == 'cold.py'
    main_file = utility.guess_mainfile('Python 3', ['cold.py'], 'cold')
    assert main_file == 'cold.py'
    main_file = utility.guess_mainfile(
        'Python 3', ['cold.py', 'cold2.py'], 'cold')
    assert main_file == 'cold.py'
    main_file = utility.guess_mainfile(
        'Python 3', ['cold2.py', 'cold.py', 'test_cold.py'], 'cold')
    assert main_file == 'cold.py'
