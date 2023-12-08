"""Download sample data and problem metadata from Kattis
    and save them to data folders.
"""

# import sys
import shutil
from typing import Any, Dict
from pathlib import Path
import requests
import yaml
from bs4 import BeautifulSoup

from .utils import config, utility
from . import settings


def create_problem_folder(problemid: str) -> Path:
    """Get existing problem folder in the current path.

    Args:
        problemid (str): problemid

    Returns:
        Path: problem folder
    """
    try:
        root_problem_folder = utility.find_problem_root_folder(
            Path.cwd(), f"{problemid}.yaml")
    except FileNotFoundError:
        root_problem_folder = Path.cwd().joinpath(problemid)
        if not root_problem_folder.exists():
            root_problem_folder.mkdir()

    return root_problem_folder


def download_html(problemid: str) -> str:
    """Get html content from Kattis problem page.

    Args:
        problemid (str): problemid
    """
    response = requests.get(settings.KATTIS_PROBLEM_URL + problemid, timeout=5)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise requests.exceptions.InvalidURL(f"Error: {response.status_code}")


def load_problem_metadata(problemid: str = '') -> Dict[Any, Any]:
    """Load problem metadata from problem folder.

    Args:
        problemid (str): problemid

    Returns:
        Dict: problem metadata
    """
    metadata: Dict[str, Any] = dict()

    filename = "*.yaml"
    if problemid:
        filename = f"{problemid}.yaml"
    try:
        # print('search ', filename, Path.cwd())
        root_problem_folder = utility.find_problem_root_folder(
            Path.cwd(), filename)
        if not problemid:
            problemid = root_problem_folder.name
    except FileNotFoundError:
        # print('file not found...')
        if not problemid:
            return metadata
        else:
            root_problem_folder = Path.cwd().joinpath(problemid)
            if not root_problem_folder.exists():
                root_problem_folder.mkdir()
    # print('root_problem_folder', root_problem_folder)
    metadata_file = root_problem_folder.joinpath(f"{problemid}.yaml")
    # print('metadata_file', metadata_file)
    if metadata_file.exists():
        with open(metadata_file, "r", encoding='utf-8') as f:
            metadata = yaml.safe_load(f)
            if 'submissions' not in metadata:
                metadata['submissions'] = 0
                metadata['accepted'] = 0
                config.update_problem_metadata(problemid, metadata)
    else:
        html = download_html(problemid)
        metadata = _parse_metadata(problemid, html)
        save_metadata(problemid, metadata)
    return metadata


def _parse_metadata(problemid: str,
                    html: str,
                    ) -> Dict[str, Any]:
    """Parse metadata from Kattis problm page.
    This function should only be called if
    the metadata file does not exist.

    Args:
        root_problem_folder (Path): problem folder
        problemid (str): Kattis problemid

    Returns:
        Dict: problem metadata
    """

    soup = BeautifulSoup(html, "html.parser")
    meta_data = {'problemid': problemid, 'title': '',
                 'cpu_limit': 'None', 'mem_limit': 'None',
                 'difficulty': 'None',
                 'submissions': 0, 'accepted': 0}

    # get the title of the problem
    title = soup.find("h1")
    if title:
        meta_data["title"] = title.text

    # get the cpu time limit, memory limit, difficulty, and source
    data = soup.find("div", {"class": "metadata-grid"})
    name_mapping = {'metadata-cpu-card': 'cpu_limit',
                    'metadata-memmory-card': 'mem_limit',
                    'metadata-difficulty-card': 'difficulty',
                    }

    for key, key1 in name_mapping.items():
        try:
            value = ''
            div = data.findChild('div', {'class': key})  # type: ignore
            if key == 'metadata-difficulty-card':
                span = div.findChild(  # type: ignore
                    'span', {
                        'class': 'difficulty_number'})
                value += span.text.strip() + ' '  # type: ignore
            span = div.findChild('span',  # type: ignore
                                 {'class': 'text-blue-200'})
            value += span.text.strip()  # type: ignore
            meta_data[key1] = value
        except AttributeError:
            pass
    return meta_data


def save_metadata(problemid: str, metadata: Dict[str, Any]) -> None:
    """Save metadata to problem folder.

    Args:
        problemid (str): problemid
        metadata (Dict[str, Any]): metadata
    """
    root_problem_folder = create_problem_folder(problemid)
    metadata_file = root_problem_folder.joinpath(f"{problemid}.yaml")
    with open(metadata_file, "w", encoding='utf-8') as f:
        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)


def download_sample_data(problemid: str) -> None:
    """Download sample data from Kattis and save them to data folders.

    Args:
        problemid (str): Kattis problem id.
    """
    uri = f'{settings.KATTIS_PROBLEM_URL}{problemid}'
    uri += '/file/statement/samples.zip'

    root_problem_folder = create_problem_folder(problemid)

    data_folder = root_problem_folder.joinpath('data')
    data_folder.mkdir(exist_ok=True)
    response = requests.get(uri, allow_redirects=True, timeout=10)
    if response.status_code == 200:
        zip_path = data_folder.joinpath('samples.zip')
        with open(data_folder.joinpath('samples.zip'), 'wb') as f:
            f.write(response.content)
        # extract zip file
        shutil.unpack_archive(zip_path, data_folder)
        zip_path.unlink()
    else:
        raise requests.exceptions.InvalidURL(f"Error: {response.status_code}")
