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
        """Test parse_config falls back to packaged defaults for known
        languages missing from the user's config file.
        """
        config_file = Path.home().joinpath(".kattis-cli.toml")
        config_file.touch()
        data = config.parse_config('c')
        self.assertEqual(data['mainfile'], '{problemid}.c')
        data = config.parse_config('java')
        self.assertEqual(data['mainfile'], '{problemid}')
        # unrecognized language falls back to config_data['default'],
        # which is missing here, so it raises KeyError
        self.assertRaises(KeyError, config.parse_config, 'c++')
        config_file.unlink()

    def test_parse_config_missing_language_falls_back_to_package(self) -> None:
        """A user config that predates a newer language (e.g. bash) should
        fall back to the packaged default instead of silently using the
        wrong language's command (e.g. running a bash script with python3).
        """
        config_file = Path.home().joinpath(".kattis-cli.toml")
        with open(config_file, "w", encoding='utf-8') as f:
            f.write(
                '[default]\ncompile = ""\n'
                'execute = "python3 {mainfile}"\n'
                'mainfile = "{problemid}.py"\n')
        data = config.parse_config('bash')
        config_file.unlink()
        self.assertEqual(data['execute'], 'bash {mainfile}')

    def test_parse_config_default(self) -> None:
        """Test parse_config function.
        """
        dest_file = Path.home().joinpath(".kattis-cli.toml")
        src_file = Path.cwd().joinpath('src/kattis_cli').\
            joinpath(".kattis-cli.toml")
        shutil.copy(src_file, dest_file)
        data = config.parse_config()
        dest_file.unlink()
        self.assertEqual(data['compile'], '')
        self.assertEqual(data['execute'], 'python3 {mainfile}')
        self.assertEqual(data['mainfile'], '{problemid}.py')
