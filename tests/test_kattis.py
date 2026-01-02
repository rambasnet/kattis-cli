"""Module to parse the HTML result from Kattis."""

import json
import os
import tempfile
import configparser
from typing import Any
from unittest import TestCase
from unittest.mock import patch, MagicMock
import requests
from kattis_cli import kattis
from kattis_cli.client import KattisClient
from kattis_cli.utils import config


class TestClient(TestCase):
    """Test Kattis client module.
    """

    def test_parse_row_html(self) -> None:
        """Test parse_row_html function.
        """
        current_path: str = os.path.dirname(os.path.realpath(__file__))
        html_file: str = os.path.join(current_path, '1.json')
        content = json.load(open(html_file, 'r', encoding='utf-8'))
        # print(content['row_html'])
        rt, st, lang, t_st, res = kattis.parse_row_html(content['row_html'])
        self.assertIsNotNone(rt)
        self.assertIsNotNone(st)
        self.assertIsNotNone(lang)
        self.assertIsNotNone(t_st)
        self.assertIsNotNone(res)


class TestSubmitSolution(TestCase):
    """Test submit_solution method of KattisClient class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = KattisClient()
        self.temp_dir: str = tempfile.mkdtemp()

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_temp_file(self, filename: str, content: str = "test") -> str:
        """Helper to create temporary files for testing."""
        filepath: str = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    def _create_mock_config(self) -> configparser.ConfigParser:
        """Create a mock Kattis config."""
        cfg = configparser.ConfigParser()
        cfg['kattis'] = {
            'hostname': 'open.kattis.com',
            'submissionurl': 'https://open.kattis.com/submit',
            'submissionsurl': 'https://open.kattis.com/submissions',
            'loginurl': 'https://open.kattis.com/login'
        }
        cfg['user'] = {
            'username': 'testuser',
            'token': 'testtoken'
        }
        return cfg

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_success(self, mock_submit: Any,
                                     mock_login_reply: Any,
                                     mock_get_config: Any) \
            -> None:
        """Test successful submission of a solution."""
        # Setup
        test_file: str = self._create_temp_file(
            "solution.py", "print('hello')")
        mock_get_config.return_value = self._create_mock_config()

        # Mock login reply
        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit response with valid submission ID
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Submission ID: 12345</html><br />'
        mock_submit.return_value = mock_response

        # Mock show_kattis_judgement to avoid running the live UI
        with patch.object(self.client, 'show_kattis_judgement'):
            # Execute
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

        # Verify
        mock_submit.assert_called_once()
        self.assertEqual(mock_submit.call_args[0][2], 'cold')  # problem id
        self.assertEqual(mock_submit.call_args[0][3], 'Python 3')  # language

    @patch('kattis_cli.client.config.get_kattisrc')
    def test_submit_solution_no_config_file(self,
                                            mock_get_config: Any) \
            -> None:
        """Test submit_solution when config file is missing."""
        # Setup
        test_file: str = self._create_temp_file("solution.py")
        mock_get_config.side_effect = config.ConfigError('Config not found')

        # Execute & Verify
        with self.assertRaises(SystemExit):
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

    @patch('kattis_cli.client.config.get_kattisrc')
    def test_submit_solution_no_files(self, mock_get_config: Any) \
            -> None:
        """Test submit_solution when no files are provided."""
        # Setup
        mock_get_config.return_value = self._create_mock_config()

        with patch.object(self.client, 'get_login_reply'):
            # Execute & Verify
            with self.assertRaises(SystemExit):
                self.client.submit_solution(
                    files=[],
                    problemid='cold',
                    language='Python 3',
                    mainclass='',
                    tag='',
                    force=True
                )

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    def test_submit_solution_file_not_found(self,
                                            mock_login_reply: Any,
                                            mock_get_config: Any) \
            -> None:
        """Test submit_solution when file does not exist."""
        # Setup
        nonexistent_file: str = os.path.join(self.temp_dir, 'nonexistent.py')
        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Execute & Verify
        with self.assertRaises(SystemExit):
            self.client.submit_solution(
                files=[nonexistent_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    def test_submit_solution_file_starts_with_digit(self,
                                                    mock_login_reply: Any,
                                                    mock_get_config: Any) \
            -> None:
        """Test submit_solution when filename starts with a digit."""
        # Setup
        test_file: str = self._create_temp_file("1solution.py")
        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Execute & Verify
        with self.assertRaises(SystemExit):
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_submit_failure_403(self,
                                                mock_submit: Any,
                                                mock_login_reply: Any,
                                                mock_get_config: Any) -> None:
        """Test submit_solution when submission fails with 403 status."""
        # Setup
        test_file: str = self._create_temp_file("solution.py")
        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit response with 403 error
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_submit.return_value = mock_response

        # Execute & Verify
        with self.assertRaises(SystemExit):
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_submit_failure_404(self,
                                                mock_submit: Any,
                                                mock_login_reply: Any,
                                                mock_get_config: Any) \
            -> None:
        """Test submit_solution when submission fails with 404 status."""
        # Setup
        test_file: str = self._create_temp_file("solution.py")
        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit response with 404 error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_submit.return_value = mock_response

        # Execute & Verify
        with self.assertRaises(SystemExit):
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_submit_connection_error(self,
                                                     mock_submit: Any,
                                                     mock_login_reply: Any,
                                                     mock_get_config: Any) \
            -> None:
        """Test submit_solution when submit connection fails."""
        # Setup
        test_file: str = self._create_temp_file("solution.py")
        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit to raise connection error
        mock_submit.side_effect = requests.exceptions.ConnectionError(
            'Connection failed')

        # Execute & Verify
        with self.assertRaises(SystemExit):
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_multiple_files(self, mock_submit: Any,
                                            mock_login_reply: Any,
                                            mock_get_config: Any) \
            -> None:
        """Test successful submission with multiple files."""
        # Setup
        test_file1: str = self._create_temp_file("solution.py")
        test_file2: str = self._create_temp_file("util.py")

        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Submission ID: 12345</html><br />'
        mock_submit.return_value = mock_response

        with patch.object(self.client, 'show_kattis_judgement'):
            # Execute
            self.client.submit_solution(
                files=[test_file1, test_file2],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

        # Verify - should be called with sorted unique files
        mock_submit.assert_called_once()
        call_files = mock_submit.call_args[0][4]
        self.assertEqual(len(call_files), 2)

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_with_duplicate_files(self, mock_submit: Any,
                                                  mock_login_reply: Any,
                                                  mock_get_config: Any) \
            -> None:
        """Test submission deduplicates file list."""
        # Setup
        test_file: str = self._create_temp_file("solution.py")

        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Submission ID: 12345</html><br />'
        mock_submit.return_value = mock_response

        with patch.object(self.client, 'show_kattis_judgement'):
            # Execute with duplicate files
            self.client.submit_solution(
                files=[test_file, test_file, test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=True
            )

        # Verify - should be called with one unique file
        mock_submit.assert_called_once()
        call_files = mock_submit.call_args[0][4]
        self.assertEqual(len(call_files), 1)

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient._confirm_or_die')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_confirm_when_not_forced(self, mock_submit: Any,
                                                     mock_confirm: Any,
                                                     mock_login_reply: Any,
                                                     mock_get_config: Any) \
            -> None:
        """Test that confirmation is requested when force=False."""
        # Setup
        test_file: str = self._create_temp_file("solution.py")
        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Submission ID: 12345</html><br />'
        mock_submit.return_value = mock_response

        with patch.object(self.client, 'show_kattis_judgement'):
            # Execute with force=False
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='',
                force=False
            )

        # Verify confirmation was called
        mock_confirm.assert_called_once()

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_with_mainclass(self,
                                            mock_submit: Any,
                                            mock_login_reply: Any,
                                            mock_get_config: Any) \
            -> None:
        """Test submission with a main class specified."""
        # Setup
        test_file: str = self._create_temp_file("Solution.java")
        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Submission ID: 12345</html><br />'
        mock_submit.return_value = mock_response

        with patch.object(self.client, 'show_kattis_judgement'):
            # Execute
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Java',
                mainclass='Solution',
                tag='',
                force=True
            )

        # Verify mainclass was passed
        mock_submit.assert_called_once()
        self.assertEqual(mock_submit.call_args[0][5], 'Solution')

    @patch('kattis_cli.client.config.get_kattisrc')
    @patch('kattis_cli.client.KattisClient.get_login_reply')
    @patch('kattis_cli.client.KattisClient.submit')
    def test_submit_solution_with_tag(self,
                                      mock_submit: Any,
                                      mock_login_reply: Any,
                                      mock_get_config: Any) \
            -> None:
        """Test submission with a tag specified."""
        # Setup
        test_file: str = self._create_temp_file("solution.py")
        mock_get_config.return_value = self._create_mock_config()

        mock_login = MagicMock()
        mock_login.cookies = {}
        mock_login_reply.return_value = mock_login

        # Mock submit response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Submission ID: 12345</html><br />'
        mock_submit.return_value = mock_response

        with patch.object(self.client, 'show_kattis_judgement'):
            # Execute
            self.client.submit_solution(
                files=[test_file],
                problemid='cold',
                language='Python 3',
                mainclass='',
                tag='attempt-1',
                force=True
            )

        # Verify tag was passed
        mock_submit.assert_called_once()
        self.assertEqual(mock_submit.call_args[0][6], 'attempt-1')
