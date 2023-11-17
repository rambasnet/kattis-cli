""" Config file parser for kattis-cli
"""

from typing import Any
from pathlib import Path
import sys
import os
import configparser
from tomlkit import load

_DEFAULT_CONFIG = Path.home().joinpath('.kattisrc')

class ConfigError(Exception):
    """Exception raised for errors in the config file."""

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
    return config_data['default']


def get_kattisrc() -> configparser.ConfigParser:
    """Returns a ConfigParser object for the .kattisrc file(s)
    """
    cfg = configparser.ConfigParser()
    if os.path.exists(_DEFAULT_CONFIG):
        cfg.read(_DEFAULT_CONFIG)

    if not cfg.read([os.path.join(os.path.expanduser("~"), '.kattisrc'),
                     os.path.join(os.path.dirname(sys.argv[0]), '.kattisrc')]):
        raise ConfigError('''\
I failed to read in a config file from your home directory or from the
same directory as this script. To download a .kattisrc file please visit
https://<kattis>/download/kattisrc

The file should look something like this:
[user]
username: yourusername
token: *********

[kattis]
hostname: <kattis>
loginurl: https://<kattis>/login
submissionurl: https://<kattis>/submit
submissionsurl: https://<kattis>/submissions''')
    return cfg
