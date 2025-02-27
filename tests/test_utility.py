"""Test the Unitlity module.
"""

from kattis_cli.utils.utility import check_answer


def test_compare_floats_single_float() -> None:
    """Test compare_floats function.
    """
    expected = '1.\n'
    ans = '1.001\n'
    places = 2
    assert check_answer(expected, ans, places) is True


def test_compare_floats_multiple_floats() -> None:
    """Test compare_floats function.
    """
    expected = '1.5555\n2.1111\n'
    ans = '1.5556\n2.1115\n'
    places = 3
    assert check_answer(expected, ans, places) is True


def test_compare_strings() -> None:
    """Test compare_floats function.
    """
    expected = 'Hello, World!\n'
    ans = 'Hello, World!\n'
    assert check_answer(expected, ans) is True


def test_compare_floats_single_float_fail() -> None:
    """Test compare_floats function.
    """
    expected = '1.001\n'
    ans = '1.011\n'
    places = 2
    assert check_answer(expected, ans, places) is False


def test_compare_floats_multiple_floats_fail() -> None:
    """Test compare_floats function.
    """
    expected = '1.5555\n2.1111\n'
    ans = '1.5556\n2.1115\n'
    places = 4
    assert check_answer(expected, ans, places) is False


def test_compare_strings_fail() -> None:
    """Test compare_floats function.
    """
    expected = 'Hello, World!\n'
    ans = 'Hello, World\n'
    assert check_answer(expected, ans) is False


def test_compare_strings_fail_2() -> None:
    """Test compare_floats function.
    """
    expected = 'Hello, World!\nGoodbye, World!\n'
    ans = 'Hello, World!\nGood bye!\n'
    assert check_answer(expected, ans) is False
