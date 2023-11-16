""" Config file parser for kattis-cli
"""

from typing import Any
from pathlib import Path
from tomlkit import load


def parse_config(language: str = '') -> Any:
    """Parse config file.

    Returns:
        Dict: config file
    """
    config_file = Path.home().joinpath(".kattis-cli.toml")
    if not config_file.exists():
        # check in current dir
        config_file = Path.cwd().joinpath(".kattis-cli.toml")
    if config_file.exists():
        with open(config_file, "r", encoding='utf-8') as f:
            config_data = load(f)
    else:
        raise FileNotFoundError(f"Config file {config_file} not found.")
    if language in config_data:
        return config_data[language]
    return config_data['default']['language']
