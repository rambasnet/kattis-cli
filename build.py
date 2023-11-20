"""
Build script for the project.
"""

from typing import Any
import shutil


def build() -> Any:
    """_summary_

    Returns:
        Any: _description_
    """
    # copy dev.py to kattis_cli/main.py
    shutil.copyfile('dev.py', 'kattis_cli/main.py')
    print('Build successful.')


if __name__ == '__main__':
    build()
