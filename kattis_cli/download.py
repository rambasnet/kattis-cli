"""Download sample data and problem metadata from Kattis and save them.

This module provides a :class:`DownloadManager` that encapsulates
the download and metadata parsing logic. For backward compatibility the
module also exposes the original functions which delegate to a default
``DownloadManager`` instance.
"""

import shutil
from typing import Any, Dict
from pathlib import Path
import requests
import yaml
from bs4 import BeautifulSoup
from .utils import config, utility
from . import settings


class DownloadManager:
    """Manager responsible for fetching problem metadata and sample data."""

    def create_problem_folder(self, problemid: str) -> Path | Any:
        """Ensure and return the root folder for a problem.

        If a problem folder cannot be resolved by searching the current
        working tree, create a new folder named after the problem id.

        Args:
            problemid: The Kattis problem id.

        Returns:
            Path to the root problem folder, or Any on failure.
        """

        try:
            root_problem_folder = utility.find_problem_root_folder(
                Path.cwd(), f"{problemid}.yaml")
        except FileNotFoundError:
            root_problem_folder = Path.cwd().joinpath(problemid)
            if not root_problem_folder.exists():
                root_problem_folder.mkdir()

        return root_problem_folder

    def download_html(self, problemid: str) -> Any:
        """Download the problem HTML page for a given problem id.

        Returns the HTML body as a stripped string when successful or
        raises an HTTP-related exception on failure.
        """

        response = requests.get(
            settings.KATTIS_PROBLEM_URL + problemid, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise requests.exceptions.InvalidURL(
                f"Error: {response.status_code}")

    def load_problem_metadata(self, problemid: str = '') -> Dict[Any, Any]:
        """Load problem metadata from disk or by scraping the problem page.

        If a local YAML metadata file is present it is loaded. Otherwise
        the problem page is downloaded and parsed, and the metadata is
        saved locally before being returned.
        """

        metadata: Dict[str, Any] = dict()

        filename = "*.yaml"
        if problemid:
            filename = f"{problemid}.yaml"
        try:
            root_problem_folder = utility.find_problem_root_folder(
                Path.cwd(), filename)
            if not problemid:
                problemid = root_problem_folder.name
        except FileNotFoundError:
            if not problemid:
                return metadata
            else:
                root_problem_folder = Path.cwd().joinpath(problemid)
                if not root_problem_folder.exists():
                    root_problem_folder.mkdir()

        metadata_file = root_problem_folder.joinpath(f"{problemid}.yaml")
        if metadata_file.exists():
            with open(metadata_file, "r", encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
                if 'submissions' not in metadata:
                    metadata['submissions'] = 0
                    metadata['accepted'] = 0
                    config.update_problem_metadata(problemid, metadata)
        else:
            html = self.download_html(problemid)
            metadata = self._parse_metadata(problemid, html)
            self.save_metadata(problemid, metadata)
        return metadata

    def _parse_metadata(self, problemid: str, html: str) -> Dict[str, Any]:
        """Internal parser that extracts metadata from problem HTML.

        This method uses BeautifulSoup to extract title, limits,
        difficulty and basic submission stats from the problem page.
        """

        soup = BeautifulSoup(html, "html.parser")
        meta_data = {'problemid': problemid, 'title': '',
                     'cpu_limit': 'None', 'mem_limit': 'None',
                     'difficulty': 'None',
                     'submissions': 0, 'accepted': 0}

        title = soup.find("h1")
        if title:
            meta_data["title"] = title.text

        data = soup.find("div", {"class": "metadata-grid"})
        name_mapping = {'metadata-cpu-card': 'cpu_limit',
                        'metadata-memmory-card': 'mem_limit',
                        'metadata-difficulty-card': 'difficulty',
                        }

        for key, key1 in name_mapping.items():
            try:
                value = ''
                # Use .find() instead of deprecated .findChild()
                div = data.find('div', {'class': key})  # type: ignore
                if key == 'metadata-difficulty-card':
                    cls = {'class': 'difficulty_number'}
                    span = div.find('span', cls)  # type: ignore
                    if span:
                        value += span.text.strip() + ' '  # type: ignore
                cls2 = {'class': 'text-blue-200'}
                span = div.find('span', cls2)  # type: ignore
                if span:
                    value += span.text.strip()  # type: ignore
                meta_data[key1] = value
            except AttributeError:
                pass
        return meta_data

    def parse_metadata(self, problemid: str, html: str) -> Dict[str, Any]:
        """Public alias for the internal metadata parser.

        Keeping a public method makes it easier for external callers and
        the compatibility wrapper to access parsing without touching a
        protected member.
        """
        return self._parse_metadata(problemid, html)

    def save_metadata(self, problemid: str, metadata: Dict[str, Any]) -> None:
        """Persist metadata dictionary to the problem YAML file."""

        root_problem_folder = self.create_problem_folder(problemid)
        metadata_file = root_problem_folder.joinpath(f"{problemid}.yaml")
        with open(metadata_file, "w", encoding='utf-8') as f:
            yaml.dump(metadata, f, default_flow_style=False,
                      allow_unicode=True)

    def download_sample_data(self, problemid: str) -> None:
        """Download the sample data zip for a problem and unpack it.

        The samples are downloaded into a `data/` folder inside the
        problem root folder and the zip is removed after extraction.
        """

        uri = f'{settings.KATTIS_PROBLEM_URL}{problemid}'
        uri += '/file/statement/samples.zip'

        response = requests.get(uri, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            root_problem_folder = self.create_problem_folder(problemid)
            data_folder = root_problem_folder.joinpath('data')
            data_folder.mkdir(exist_ok=True)
            zip_path = data_folder.joinpath('samples.zip')
            with open(data_folder.joinpath('samples.zip'), 'wb') as f:
                f.write(response.content)
            shutil.unpack_archive(zip_path, data_folder)
            zip_path.unlink()
        else:
            raise requests.exceptions.InvalidURL(
                f"Error: {response.status_code}")


# Default manager instance for compatibility with existing imports
_manager = DownloadManager()


def create_problem_folder(problemid: str) -> Path:
    """Module-level wrapper returning the problem root folder.

    Delegates to the default :class:`DownloadManager` instance so code
    using the previous functional API continues to work.
    """

    return _manager.create_problem_folder(problemid)


def download_html(problemid: str) -> Any:
    """Download problem HTML using the module-level manager."""

    return _manager.download_html(problemid)


def load_problem_metadata(problemid: str = '') -> Dict[Any, Any]:
    """Load problem metadata via the default DownloadManager."""

    return _manager.load_problem_metadata(problemid)


def save_metadata(problemid: str, metadata: Dict[str, Any]) -> None:
    """Persist metadata using the default DownloadManager."""

    return _manager.save_metadata(problemid, metadata)


def download_sample_data(problemid: str) -> None:
    """Download and unpack sample data using the default manager."""

    return _manager.download_sample_data(problemid)


def _parse_metadata(problemid: str, html: str) -> Dict[str, Any]:
    """Compatibility wrapper for the legacy module-level helper used by
    tests. Delegates to the DownloadManager implementation.
    """
    # Prefer the public API on the manager to avoid accessing a protected
    # member from outside the class.
    return _manager.parse_metadata(problemid, html)
