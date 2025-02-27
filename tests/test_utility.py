"""Test the Unitlity module.
"""

from kattis_cli.utils.utility import compare_floats


def test_compare_floats_single() -> None:
    """Test compare_floats function.
    """
    expected = '1.\n'
    ans = '1.001\n'
    places = 2
    assert compare_floats(expected, ans, places) is True


def test_compare_floats_multiple() -> None:
    """Test compare_floats function.
    """
    expected = '1.5555\n2.1111\n'
    ans = '1.5556\n2.1115\n'
    places = 3
    assert compare_floats(expected, ans, places) is True
