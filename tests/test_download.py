"""Module to test the download module.
"""

import unittest
from pathlib import Path
import shutil
import requests
from kattis_cli.utils import utility
from kattis_cli import download


class TestDownload(unittest.TestCase):
    """Class to test the download module.
    """

    def test_find_problem_root_folder_exception(self) -> None:
        """Test get_problem_root_folder function.
        """
        self.assertRaises(
            FileNotFoundError,
            utility.find_problem_root_folder,
            Path.cwd(),
            "*.yaml")

    def test_get_problem_root_folder(self) -> None:
        """Test get_problem_root_folder function.
        """
        folder = 'hello'
        path = Path.cwd().joinpath(folder)
        path.mkdir(exist_ok=True)
        path.joinpath('hello.yaml').touch()
        root_folder = utility.find_problem_root_folder(path, "*.yaml")
        self.assertEqual(root_folder, path)
        shutil.rmtree(path)

    def test_create_problem_folder(self) -> None:
        """Test check_problem_folder function.
        """
        folder = 'cold'
        download.create_problem_folder(folder)
        self.assertTrue(Path.cwd().joinpath(folder).exists())
        shutil.rmtree(Path.cwd().joinpath(folder))

        folder = 'hello'
        download.create_problem_folder(folder)
        self.assertTrue(Path.cwd().joinpath(folder).exists())
        shutil.rmtree(Path.cwd().joinpath(folder))

    def test_make_soup(self) -> None:
        """Test make_soup function.
        """
        self.assertRaises(
            requests.exceptions.InvalidURL,
            download.make_soup,
            "123blah")
        self.assertRaises(
            requests.exceptions.InvalidURL,
            download.make_soup,
            "123blahblah")

    def test_download_sample_data_exception(self) -> None:
        """Test download_sample_data.
        """
        problemid = '123blah'
        self.assertRaises(
            requests.exceptions.InvalidURL,
            download.download_sample_data,
            problemid)
        shutil.rmtree(Path.cwd().joinpath(problemid))
        problemid = '123blahblah'
        self.assertRaises(
            requests.exceptions.InvalidURL,
            download.download_sample_data,
            problemid)
        shutil.rmtree(Path.cwd().joinpath(problemid))

    def test_download_sample_data(self) -> None:
        """Test download_sample_data.
        """
        problemid = 'cold'
        download.download_sample_data(problemid)
        folder = Path.cwd().joinpath(problemid)
        self.assertTrue(folder.exists())
        shutil.rmtree(folder)

    def test_load_meta_data(self) -> None:
        """Test load_meta_data.
        """
        problemid = 'cold'
        metadata = download.load_problem_metadata()
        self.assertDictEqual(metadata, {})
        download.download_sample_data(problemid)
        metadata = download.load_problem_metadata(problemid)
        # print(metadata)
        self.assertEqual(metadata['problemid'], problemid)
        self.assertTrue(Path.cwd().joinpath(
            problemid).joinpath(f'{problemid}.yaml').exists())
        shutil.rmtree(Path.cwd().joinpath(problemid))
