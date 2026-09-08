""" Config file parser for kattis-cli
"""

from typing import Any, Dict
from pathlib import Path
import sys
import os
import configparser
from tomlkit import load
import yaml

from kattis_cli.utils.utility import find_problem_root_folder

_KATTIS_RC = Path.home().joinpath('.kattisrc')
# packaged config shipped with kattis-cli, used as a fallback when the
# user's own config file predates a newly supported language (e.g. bash)
_PACKAGE_CONFIG = Path(__file__).resolve().parent.parent.joinpath(
    ".kattis-cli.toml")


class ConfigError(Exception):
    """Exception raised for errors in the config file."""


def _load_toml(path: Path) -> Any:
    with open(path, "r", encoding='utf-8') as f:
        return load(f)


def parse_config(language: str = '') -> Any:
    """Parse toml config file.

    Returns:
        Dict: toml file.
    """
    config_file = Path.home().joinpath(".kattis-cli.toml")
    if not config_file.exists():
        # check in current dir
        config_file = Path.cwd().joinpath(".kattis-cli.toml")
    if config_file.exists():
        config_data = _load_toml(config_file)
    else:
        raise FileNotFoundError(f"Config file {config_file} not found.")
    if language in config_data:
        return config_data[language]
    # user's config file may predate this language being added; fall
    # back to the packaged defaults instead of silently using [default]
    if language and _PACKAGE_CONFIG.exists():
        package_data = _load_toml(_PACKAGE_CONFIG)
        if language in package_data:
            return package_data[language]
    return config_data['default']


def get_kattisrc() -> configparser.ConfigParser:
    """Returns a ConfigParser object for the .kattisrc file(s)
    """
    cfg = configparser.ConfigParser()
    if os.path.exists(_KATTIS_RC):
        cfg.read(_KATTIS_RC)

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


def update_problem_metadata(problemid: str, metadata: Dict[Any, Any]) -> None:
    """Update problem.yaml file.
    """
    root_problem_folder = find_problem_root_folder(Path.cwd(),
                                                   f'{problemid}.yaml')
    yaml_file = Path.joinpath(root_problem_folder, f'{problemid}.yaml')
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, default_flow_style=False)
