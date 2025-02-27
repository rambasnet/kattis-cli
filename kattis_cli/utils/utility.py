""" Utility functions. """

from pathlib import Path
import os
from typing import Union
import yaml


def find_problem_root_folder(
    cur_dir_path: Union[str, Path],
    filename: str
) -> Path:
    """Find the root problem folder given a directory path and filename.

    Args:
        cur_dir_path (Union[str, Path]): String or Path
            object of directory path
        filename (str): filename to search for
            including wildcard pattern

    Returns:
        Path: Path object of the root problem folder
    """

    def _check_file_match_folder(path: Path, filename: str) -> bool:
        """ Check folder is same name as the filename given
        filename including wildcard.

        Args:
            path (Path): Path object of directory path
            filename (str): filename to search for
                including wildcard pattern
        Returns:
            bool: True if path exists, False otherwise
        """
        for file in path.glob(filename):
            name, ext = os.path.splitext(file.name)
            folder_name = path.parts[-1]
            # print(f'{name} {folder_name=} {name=} {ext=}')
            if name == folder_name:
                return True
            # read yaml file
            if ext == '.yaml':
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if 'problemid' in data:
                        return True
        return False

    # print(f'{cur_dir_path=} {filename=}')
    if not filename:
        filename = '.yaml'
    cur_path = Path(cur_dir_path)
    if _check_file_match_folder(cur_path, filename):
        return cur_path
    for parent in cur_path.parents:
        # print('parent', parent, file=sys.stderr)
        if _check_file_match_folder(parent, filename):
            return parent
    raise FileNotFoundError("Error: Problem root folder not found.")


def compare_floats(expected: str, ans: str, places: float) -> bool:
    """Compare two floating point numbers with given accuracy.

    Args:
        expected (str): expected result
        ans (str): actual result
        places (float): decimal places for approximation

    Returns:
        bool: True if the two numbers are equal within the given accuracy
    """
    expect_ans = expected.strip().split('\n')
    actual_ans = ans.strip().split('\n')
    if len(expect_ans) != len(actual_ans):
        return False
    try:
        for i, ex_ans in enumerate(expect_ans):
            flt_expected = float(ex_ans)
            flt_ans = float(actual_ans[i])
            if abs(flt_expected - flt_ans) > 10**(-places):
                return False
        return True
    except ValueError:
        return False
