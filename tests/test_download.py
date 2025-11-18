"""Module to test the download module.
"""

import os
import unittest
from pathlib import Path
import shutil
import requests
from kattis_cli.utils import languages
from kattis_cli import download


class TestDownload(unittest.TestCase):
    """Class to test the download module.
    """

    def test_find_problem_root_folder_exception(self) -> None:
        """Test get_problem_root_folder function.
        """
        self.assertRaises(
            FileNotFoundError,
            languages.find_problem_root_folder,
            Path.cwd(),
            "*.yaml")

    def test_get_problem_root_folder(self) -> None:
        """Test get_problem_root_folder function.
        """
        folder = 'hello'
        path = Path.cwd().joinpath(folder)
        path.mkdir(exist_ok=True)
        path.joinpath('hello.yaml').touch()
        root_folder = languages.find_problem_root_folder(path, "*.yaml")
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

    def test_download_html_exception(self) -> None:
        """Test make_soup function.
        """
        self.assertRaises(
            requests.exceptions.InvalidURL,
            download.download_html,
            "123blah")
        self.assertRaises(
            requests.exceptions.InvalidURL,
            download.download_html,
            "123blahblah")

    def test_download_sample_data_exception(self) -> None:
        """Test download_sample_data.
        """
        problemid = '123blah'
        self.assertRaises(
            requests.exceptions.InvalidURL,
            download.download_sample_data,
            problemid)
        assert Path.cwd().joinpath(problemid).exists() is False
        problemid = '123blahblah'
        self.assertRaises(
            requests.exceptions.InvalidURL,
            download.download_sample_data,
            problemid)
        assert Path.cwd().joinpath(problemid).exists() is False

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

    def test_parse_metadata_success1(self) -> None:
        """Test download_problem.
        """
        print(os.getenv('PYTEST_CURRENT_TEST'))
        problemid = 'karlcoder'
        test_file = Path.cwd().joinpath('tests').joinpath('karlcoder.html')
        with open(test_file, 'r', encoding='utf-8') as f:
            html = f.read()
        # pylint: disable=protected-access
        metadata = download._parse_metadata(problemid, html)
        # print(metadata)
        self.assertEqual(metadata['problemid'], problemid)
        self.assertEqual(metadata['title'], 'Karl Coder')
        self.assertEqual(metadata['cpu_limit'], '1 second')
        self.assertEqual(metadata['mem_limit'], '1024 MB')
        self.assertEqual(metadata['submissions'], 0)
        self.assertEqual(metadata['difficulty'], '4.0 Medium')
        self.assertEqual(metadata['accepted'], 0)

    def test_parse_metadata_success2(self) -> None:
        """Test download_problem.
        """
        # print(os.getenv('PYTEST_CURRENT_TEST'))
        problemid = 'prinsesse'
        test_file = Path.cwd().joinpath('tests').joinpath('prinsesse.html')
        with open(test_file, 'r', encoding='utf-8') as f:
            html = f.read()
        # pylint: disable=protected-access
        metadata = download._parse_metadata(problemid, html)
        # print(metadata)
        self.assertEqual(metadata['problemid'], problemid)
        self.assertEqual(metadata['title'], 'The Princess and the Pea')
        self.assertEqual(metadata['cpu_limit'], '1 second')
        self.assertEqual(metadata['mem_limit'], '1024 MB')
        self.assertEqual(metadata['submissions'], 0)
        self.assertEqual(
            metadata['difficulty'],
            '1.8\n                                                - 7.2 Hard')
        self.assertEqual(metadata['accepted'], 0)
