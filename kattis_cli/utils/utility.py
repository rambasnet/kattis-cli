"""Module for language utilities.
"""

from typing import List, Union, Any
import sys
import os
import re
from pathlib import Path
import yaml
from rich.console import Console
from kattis_cli.utils import config


KATTIS_LANGUAGE_GUESS = {
    '.c': 'C',
    '.c++': 'C++',
    '.cc': 'C++',
    '.c#': 'C#',
    '.cpp': 'C++',
    '.cs': 'C#',
    '.cxx': 'C++',
    '.cbl': 'COBOL',
    '.cob': 'COBOL',
    '.cpy': 'COBOL',
    '.fs': 'F#',
    '.go': 'Go',
    '.hs': 'Haskell',
    '.java': 'Java',
    '.js': 'JavaScript (Node.js)',
    '.ts': 'TypeScript',
    '.kt': 'Kotlin',
    '.lisp': 'Common Lisp',
    '.cl': 'Common Lisp',
    '.m': 'Objective-C',
    '.ml': 'OCaml',
    '.pas': 'Pascal',
    '.php': 'PHP',
    '.pl': 'Prolog',
    '.py': 'Python 3',
    '.rb': 'Ruby',
    '.rs': 'Rust',
    '.scala': 'Scala',
    '.f90': 'Fortran',
    '.f': 'Fortran',
    '.for': 'Fortran',
    '.sh': 'Bash',
    '.apl': 'APL',
    '.ss': 'Gerbil',
    '.jl': 'Julia',
    '.vb': 'Visual Basic',
    '.dart': 'Dart',
    '.zig': 'Zig',
    '.swift': 'Swift',
    '.nim': 'Nim',
}

GUESS_MAINCLASS = {'Java', 'Kotlin', 'Scala'}
GUESS_MAINFILE = {
    'APL',
    'Bash',
    'Dart',
    'Gerbil',
    'JavaScript (Node.js)',
    'Julia',
    'Common Lisp',
    'Pascal',
    'PHP',
    'Python 2',
    'Python 3',
    'Ruby',
    'Rust',
    'TypeScript',
    'Zig'
}

LOCAL_LANGUAGES = {
    'Python 3': 'python3',
    'C++': 'c++'
}


def guess_language(ext: str, files: List[str]) -> str:
    """Guess the language.

    Args:
        ext (str): File extension.
        files (List[str]): Tuple of files.

    Returns:
        str: guessed language
    """
    if ext == ".C":
        return "C++"
    ext = ext.lower()
    if ext == ".h":
        if any(f.endswith(".c") for f in files):
            return "C"
        else:
            return "C++"
    if ext == ".py":
        if is_python2(files):
            return "Python 2"
        else:
            return "Python 3"
    return KATTIS_LANGUAGE_GUESS.get(ext, '')


def is_python2(files: List[str]) -> bool:
    """Check if python2.

    Args:
        files (List[str]): Tuple of files.

    Returns:
       bool: True if python2, False otherwise.
    """
    python2 = re.compile(r'^\s*\bprint\b *[^ \(\),\]]|\braw_input\b')
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for index, line in enumerate(f):
                    # print(index, line)
                    if index == 0 and line.startswith('#!'):
                        if 'python2' in line:
                            return True
                        if 'python3' in line:
                            return False
                    if python2.search(line.split('#')[0]):
                        return True
        except IOError:
            return False
    return False


def guess_mainfile(
        language: str,
        files: List[str],
        problemid: str) -> Any:
    """Guess the main file.

    Args:
        language (str): programming language
        files (List[str]): Tuple of files

    Returns:
        str: main file
    """
    if len(files) == 1:
        return files[0]
    # check .kattis-cli.toml file
    config_data = config.parse_config(language)
    if 'mainfile' in config_data:
        return config_data['mainfile'].replace(('<problemid>'), problemid)
    for filename in files:
        if os.path.splitext(os.path.basename(filename))[0] in ['main', 'Main']:
            return filename
        if problemid and os.path.splitext(
                os.path.basename(filename))[0] == problemid:
            return filename
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                conts = f.read()
                if language in [
                        'Java', 'Rust', 'Scala', 'Kotlin'] and re.search(
                        r' main\s*\(', conts):
                    return filename
                if language == 'Pascal' and re.match(
                        r'^\s*[Pp]rogram\b', conts):
                    return filename
        except IOError:
            pass
    # main file is the one with problemid
    return files[0]


def guess_mainclass(problemid: str, language: str, files: List[str]) -> Any:
    """Guess the main class.

    Args:
        language (str): programming language
        files (Tuple[str]): Tuple of files

    Returns:
        str: main class
    """
    if language in GUESS_MAINFILE and len(files) > 1:
        return os.path.basename(guess_mainfile(language, files, problemid))
    if language in GUESS_MAINCLASS:
        mainfile = os.path.basename(guess_mainfile(language, files, problemid))
        name = os.path.splitext(mainfile)[0]
        if language == 'Kotlin':
            return name[0].upper() + name[1:] + 'Kt'
        return name
    return ''


def valididate_language(language: str) -> bool:
    """Check if valid language.

    Args:
        language (str): programming language

    Returns:
        bool: True if valid language, exit otherwise.
    """
    if language in KATTIS_LANGUAGE_GUESS.values():
        return True
    console = Console()
    console.print(f'Invalid language: "{language}"', style='bold red')
    console.print('Valid languages are:', style='bold green')
    for lang in sorted(list(set(KATTIS_LANGUAGE_GUESS.values()))):
        console.print(f'\t\t - {lang}')
    exit(1)


def valid_extension(file: str) -> bool:
    """Check if valid extension.

    Args:
        ext (str): File extension.

    Returns:
        bool: True if valid extension, exit otherwise.
    """
    if os.path.isfile(file):
        ext = os.path.splitext(file)
        if len(ext) != 2:
            return False
        return ext[1] in KATTIS_LANGUAGE_GUESS
    return False


def find_problem_root_folder(
    cur_dir_path: Union[str, Path],
    filename: str
) -> Path:
    """Find the root problem folder given a directory path and filename.

    Args:
        cur_dir_path (Union[str, Path]): String or Path
            object of directory path
        filename (str): filename to search for
            including wildcard pattern

    Returns:
        Path: Path object of the root problem folder
    """

    def _check_file_match_folder(path: Path, filename: str) -> bool:
        """ Check folder is same name as the filename given
        filename including wildcard.

        Args:
            path (Path): Path object of directory path
            filename (str): filename to search for
                including wildcard pattern
        Returns:
            bool: True if path exists, False otherwise
        """
        for file in path.glob(filename):
            name, ext = os.path.splitext(file.name)
            folder_name = path.parts[-1]
            # print(f'{name} {folder_name=} {name=} {ext=}')
            if name == folder_name:
                return True
            # read yaml file
            if ext == '.yaml':
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if 'problemid' in data:
                        return True
        return False

    # print(f'{cur_dir_path=} {filename=}')
    if not filename:
        filename = '.yaml'
    cur_path = Path(cur_dir_path)
    if _check_file_match_folder(cur_path, filename):
        return cur_path
    for parent in cur_path.parents:
        # print('parent', parent, file=sys.stderr)
        if _check_file_match_folder(parent, filename):
            return parent
    raise FileNotFoundError("Error: Problem root folder not found.")


def update_args(problemid: str,
                language: str,
                mainclass: str,
                files: List[str]) -> Any:
    """Check if problemid, language, mainclass, and program files are valid.

    Args:
        problemid (str): problemid
        language (str): programming language
        mainclass (str): main class
        files (List[str]): List of files
        root_folder (str): root folder

    Returns:
        Tuple[str]: Update problemid, language, mainclass, and files
    """
    console = Console()
    if not files:
        files = get_coding_files()
    # check if problemid is given
    # if not problemid:
    cur_folder = Path.cwd()
    root_folder = Path.cwd()
    if not problemid:
        for f in files:
            try:
                root_folder = find_problem_root_folder(
                    cur_folder, f.lower())
                # if not problemid:
                problemid = root_folder.name
                break
            except FileNotFoundError:
                # print(ex)
                pass
    if not problemid:
        try:
            root_folder = find_problem_root_folder(
                cur_folder, '*.yaml')
            problemid = root_folder.name
        except FileNotFoundError:
            console.print(f'''No problemid specified and I failed to guess
problemid and root problem folder from filename(s) and cwd: {cur_folder}.''',
                          style='bold red')
            sys.exit(1)
    # check if language
    if not language:
        _, ext = os.path.splitext(os.path.basename(files[0]))
        # Guess language from files
        language = guess_language(ext, files)
        if not language:
            console.print(f'''\
No language specified, and I failed to guess language from
filename extension "{ext}"''')
            sys.exit(1)
    # check if valid language
    valididate_language(language)
    if not mainclass:
        mainclass = guess_mainclass(problemid, language, files)
    # print(f'Returning...{problemid=} {language=} {mainclass=} {files=}')
    return problemid, language, mainclass, files, root_folder


def get_coding_files() -> List[str]:
    """Get coding files from current directory.

    Returns:
        List[str]: List of coding files.
    """
    cur_folder = str(Path.cwd())
    console = Console()
    files = [
        f for f in os.listdir(cur_folder) if valid_extension(f)]
    if not files:
        console.print(
            'No source file(s) found in the current folder!',
            style='bold red')
        exit(1)
    return files
