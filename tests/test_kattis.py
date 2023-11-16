"""Module to parse the HTML result from Kattis."""

import json
import os
from kattis_cli import kattis


def test_parse_row_html() -> None:
    """Test parse_row_html function.
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    html_file = os.path.join(current_path, '1.json')
    content = json.load(open(html_file, 'r', encoding='utf-8'))
    # print(content['row_html'])
    rt, st, lang, t_st, res = kattis.parse_row_html(content['row_html'])
    assert rt is not None
    assert st is not None
    assert lang is not None
    assert t_st is not None
    assert res is not None
