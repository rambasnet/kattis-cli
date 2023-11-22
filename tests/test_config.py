"""Test the config module.
"""


import unittest
from pathlib import Path
import shutil

from kattis_cli.utils import config


class TestConfig(unittest.TestCase):
    """Class to test the config module.
    """

    def test_parse_config_filenot_found(self) -> None:
        """Test parse_config function.
        """
        config_file = Path.home().joinpath(".kattis-cli.toml")
        if config_file.exists():
            config_file.unlink()
        self.assertRaises(FileNotFoundError, config.parse_config, 'c')
        self.assertRaises(FileNotFoundError, config.parse_config, 'c++')
        self.assertRaises(FileNotFoundError, config.parse_config, 'java')

    def test_parse_config_empty_file(self) -> None:
        """Test parse_config function.
        """
        config_file = Path.home().joinpath(".kattis-cli.toml")
        config_file.touch()
        self.assertRaises(KeyError, config.parse_config, 'c')
        self.assertRaises(KeyError, config.parse_config, 'c++')
        self.assertRaises(KeyError, config.parse_config, 'java')
        config_file.unlink()

    def test_parse_config_default(self) -> None:
        """Test parse_config function.
        """
        dest_file = Path.home().joinpath(".kattis-cli.toml")
        src_file = Path.cwd().joinpath('kattis_cli').\
            joinpath(".kattis-cli.toml")
        shutil.copy(src_file, dest_file)
        data = config.parse_config()
        dest_file.unlink()
        self.assertEqual(data['compile'], '')
        self.assertEqual(data['execute'], 'python3 {mainfile}')
        self.assertEqual(data['mainfile'], '{problemid}.py')
