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
        metadata = _download_metadata(root_problem_folder, problemid)
    return metadata


def make_soup(problemid: str) -> BeautifulSoup:
    """Scrape kattis page given problemid and return a BeautifulSoup object.

    Args:
        problemid (str): problemid

    Returns:
        BeautifulSoup: BeautifulSoup object of the problem page.
    """
    response = requests.get(settings.KATTIS_PROBLEM_URL + problemid, timeout=5)
    if response.status_code == 200:
        return BeautifulSoup(response.text.strip(), "html.parser")
    else:
        raise requests.exceptions.InvalidURL(f"Error: {response.status_code}")


def _download_metadata(root_problem_folder: Path,
                       problemid: str) -> Dict[str, Any]:
    """Download problem metadata from Kattis and save them to problem folder.
    This function should only be called if the metadata file does not exist.

    Args:
        problemid (str): Kattis problemid

    Returns:
        Dict: problem metadata
    """

    soup = make_soup(problemid)

    meta_data = {'problemid': problemid, 'title': '',
                 'cpu_limit': 'None', 'mem_limit': 'None',
                 'difficulty': 'None', 'source': 'None',
                 'submissions': 0, 'accepted': 0}

    # get the title of the problem
    title = soup.find("h1")
    if title:
        meta_data["title"] = title.text

    # get the cpu time limit, memory limit, difficulty, and source
    data = soup.find_all("div", {"class": "metadata_list-item"})
    name_mapping = {'cpu_limit': 'cpu_limit',
                    'mem_limit': 'mem_limit',
                    'difficulty': 'difficulty',
                    'source': 'source',
                    }
    for item in data:
        try:
            data_name = item.attrs['data-name'].split('-')[1]
            if data_name in name_mapping:
                children = item.findChildren('span')
                meta_data[name_mapping[data_name]] = children[-1].text.strip()
        except BaseException:
            pass

    # save metadata to file
    metadata_file = root_problem_folder.joinpath(f"{problemid}.yaml")
    with open(metadata_file, "w", encoding='utf-8') as f:
        yaml.dump(meta_data, f, default_flow_style=False, allow_unicode=True)
    return meta_data


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
