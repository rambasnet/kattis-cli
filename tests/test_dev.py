# Test file for dev.py
# dev.py contains the main CLI code which is copied to main.py during build.sh
# We will test the 'get' command for downloading sample data and metadata.


from unittest.mock import patch
import requests
from click.testing import CliRunner
import kattis_cli.main as main


def test_get_success() -> None:
    """Test the 'get' command of the CLI for successful download."""
    runner = CliRunner()

    with patch("kattis_cli.download.download_sample_data") as mock_sample, \
            patch("kattis_cli.download.load_problem_metadata") as mock_meta:

        result = runner.invoke(main.main, ["get", "cold"])

        assert result.exit_code == 0
        mock_sample.assert_called_once_with("cold")
        mock_meta.assert_called_once_with("cold")
        assert "Downloading samples" in result.output
        assert "Downloading metadata" in result.output


def test_get_invalid_url() -> None:
    """Test the 'get' command of the CLI for invalid URL handling."""
    runner = CliRunner()

    with patch("kattis_cli.download.download_sample_data",
               side_effect=requests.exceptions.InvalidURL):

        result = runner.invoke(main.main, ["get", "1invalid_problem2"])

        assert result.exit_code == 0
        assert "not found" in result.output
