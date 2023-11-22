#!/usr/bin/env python
"""
Module for submitting solutions to Kattis
https://github.com/Kattis/kattis-cli/blob/master/submit.py
"""

from typing import List, Any
import sys
import os
import re
import time
import json
import configparser
from bs4 import BeautifulSoup
import requests
import requests.exceptions
import requests.cookies
from rich.console import Console
from rich.align import Align
from rich.live import Live
from rich.prompt import Confirm

from kattis_cli.utils import utility
from kattis_cli.utils import config
from kattis_cli import ui

_HEADERS = {'User-Agent': 'kattis-cli-submit'}

_RUNNING_STATUS = 5
_COMPILE_ERROR_STATUS = 8
_ACCEPTED_STATUS = 16
_DEBUG = False

_STATUS_MAP = {
    0: 'New',  # <invalid value>
    1: 'New',
    2: 'Waiting for compile',
    3: 'Compiling',
    4: 'Waiting for run',
    _RUNNING_STATUS: 'Running',
    6: 'Judge Error',
    7: 'Submission Error',
    _COMPILE_ERROR_STATUS: 'Compile Error',
    9: 'Run Time Error',
    10: 'Memory Limit Exceeded',
    11: 'Output Limit Exceeded',
    12: 'Time Limit Exceeded',
    13: 'Illegal Function',
    14: 'Wrong Answer',
    # 15: '<invalid value>',
    _ACCEPTED_STATUS: 'Accepted',
}


def get_url(cfg: configparser.ConfigParser, option: str, default: str) -> str:
    """Get a URL from the config file

    Args:
        cfg (configparser.ConfigParser): _description_
        option (str): option name
        default (str): default value

    Returns:
        str: _description_
    """
    if cfg.has_option('kattis', option):
        return cfg.get('kattis', option)
    else:
        return f"https://{cfg.get('kattis', 'hostname')}/{default}"


def login(
        login_url: str,
        username: str,
        password: str = '',
        token: str = '') -> requests.Response:
    """Log in to Kattis.

    At least one of password or token needs to be provided.

    Args:
        login_url (str): URL to login page
        username (str): username
        password (str, optional): password. Defaults to ''
        token (str, optional): token. Defaults to ''

    Returns a requests.Response with cookies needed to be able to submit
    """
    login_args = {'user': username, 'script': 'true'}
    if password:
        login_args['password'] = password
    if token:
        login_args['token'] = token

    return requests.post(
        login_url,
        data=login_args,
        headers=_HEADERS,
        timeout=10)


def login_from_config(cfg: configparser.ConfigParser) -> requests.Response:
    """Log in to Kattis using the access information in a kattisrc file

    Args:
        cfg (configparser.ConfigParser)
         - ConfigParser object for the kattisrc file
    Returns:
        requests (requests.Response)
        - Response with cookies needed to be able to submit
    """
    username = cfg.get('user', 'username')
    password = token = ''
    try:
        password = cfg.get('user', 'password')
    except configparser.NoOptionError:
        pass
    try:
        token = cfg.get('user', 'token')
    except configparser.NoOptionError:
        pass
    if not password and not token:
        raise config.ConfigError('''\
Your .kattisrc file appears corrupted. It must provide a token (or a
KATTIS password).

Please download a new .kattisrc file''')

    loginurl = get_url(cfg, 'loginurl', 'login')
    return login(loginurl, username, password, token)


def submit(
        submit_url: str,
        cookies: requests.cookies.RequestsCookieJar,
        problem: str,
        language: str,
        files: List[str],
        mainclass: str,
        tag: str) -> requests.Response:
    """Make a submission.

    The url_opener argument is an OpenerDirector object to use (as
    returned by the login() function)

    Returns the requests.Result from the submission
    """
    # mainfile = utility.guess_mainfile(language, files, problem)
    # mainclass = mainfile

    data = {'submit': 'true',
            'submit_ctr': 2,
            'language': language,
            'mainclass': mainclass,
            'problem': problem,
            'tag': tag,
            'script': 'true'}

    sub_files = []
    for f in files:
        with open(f, 'rb') as sub_file:
            sub_files.append(('sub_file[]',
                              (os.path.basename(f),
                               sub_file.read(),
                               'application/octet-stream')))

    return requests.post(
        submit_url,
        data=data,
        files=sub_files,
        cookies=cookies,
        headers=_HEADERS, timeout=10)


def confirm_or_die(problem: str, language: str,
                   files: List[str], mainclass: str,
                   tag: str) -> None:
    """Confirm submission"""
    console = Console()
    console.clear()
    console.print('Problem:', problem)
    console.print('Language:', language)
    console.print('Files:', ', '.join(files))
    if mainclass:
        if language in utility.GUESS_MAINFILE:
            console.print('Main file:', mainclass)
        else:
            console.print('Mainclass:', mainclass)
    if tag:
        console.print('Tag:', tag)
    if not Confirm.ask('Submit to Kattis', default=True):
        console.print('Cancelling...')
        sys.exit(1)


def get_submission_url(submit_response: str,
                       cfg: configparser.ConfigParser
                       ) -> str:
    """Get the URL of the submission from the HTML response
    """
    m = re.search(r'Submission ID: (\d+)', submit_response)
    if m:
        submissions_url = get_url(cfg, 'submissionsurl', 'submissions')
        submission_id = m.group(1)
        return f'{submissions_url}/{submission_id}'
    else:
        raise config.ConfigError('Could not find submission ID in response')


def get_submission_status(
        submission_url: str,
        cookies: requests.cookies.RequestsCookieJar
) -> Any:
    """Get judge status for a submission"""
    reply = requests.get(
        submission_url + '?json',
        cookies=cookies,
        headers=_HEADERS, timeout=10)
    return reply.json()


def parse_row_html(html: str) -> Any:
    """Parse row_html value from Kattis JASON response.

    Args:
        html (str): html string

    Returns:
        Tuple: runtime, status, language, total_cases, done_cases
    """
    # print(html)
    runtime = '❓ s'
    status = '❓'
    language = '❓'
    test_status = '❓/❓'
    soup = BeautifulSoup(html, 'html.parser')
    tr_submission: Any = soup.find("tr", {"data-submission-id": True})
    # print(tr_submission)
    if tr_submission:
        td_cputime = tr_submission.findChild("td", {"data-type": "cpu"})
        if td_cputime:
            runtime = td_cputime.text.strip().replace('&nbsp;', ' ')
        if not runtime:
            runtime = '❓ s'
        div_status = tr_submission.findChild(
            "div", {"class": "status"}, recursive=True)
        if div_status:
            status = div_status.text.strip()
        else:
            status = '❓'
        td_lang = tr_submission.findChild(
            "td", {"data-type": "lang"}, recursive=False)
        if td_lang:
            language = td_lang.text.strip()
        else:
            language = '❓'
        td_test_cases = tr_submission.findChild(
            "td", {"data-type": "testcases"})
        if td_test_cases:
            test_status = td_test_cases.text.strip()

    i_tag = soup.findAll("i", {"class": True})
    test_result = []
    for num, i in enumerate(i_tag):
        if 'title' not in i.attrs:
            continue
        title = i['title'].split(':')
        # print(title[-1])
        if 'Accepted' in title[-1]:  # Accepted
            test_result.append(f'{num}✅')
        elif 'not checked' in title[-1]:  # not checked
            test_result.append(f'{num}❓')
        else:
            test_result.append(f'{num}❌')
    return runtime, status, language, test_status, test_result


def show_kattis_judgement(problemid: str, submission_url: str,
                          cfg: configparser.ConfigParser) -> None:
    """Show judgement from Kattis.
    """
    config_data = ui.show_problem_metadata(problemid)
    config_data['submissions'] += 1
    console = Console()
    login_reply = login_from_config(cfg)
    title = '\n[bold blue]                           '
    title += ':cat: Kattis Judgement Results :cat:[/]\n'
    status_id = 0
    with Live(console=console, screen=False,
              refresh_per_second=10) as kattis_live:
        counter = 1
        while True:
            time.sleep(0.1)
            result = get_submission_status(submission_url,
                                           login_reply.cookies)
            if _DEBUG:
                with open(f'{counter}.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4)
            rt, status, lang, t_status, t_results = parse_row_html(
                result['row_html'])
            # console.print(f'{runtime=} {status=} {language=}')
            status_id = int(result['status_id'])
            # cases_done = int(result['testcase_index'])
            if status_id > 4 and status_id < 16:
                judgement = f'[bold red] {status}[/]'
            else:
                judgement = f'[bold yellow] {status}[/]'
            if status_id == 12:
                runtime = f'[bold red] {rt}[/]'
            else:
                runtime = f'[bold yellow] {rt}[/]'

            text = title + f'\n[bold blue]JUDGEMENT:[/] {judgement}'
            text += f'\t[bold blue]LANGUAGE:[/] [bold yellow]{lang}[/]'
            text += f'\t[bold blue]RUNTIME:[/] {runtime}'
            text += f'\t[bold deep_pink3][link={submission_url}]'
            text += 'VIEW DETAILS ON KATTIS[/link][/]\n\n'
            text += f'[bold blue]TESTCASES:[/] [bold green]{t_status}[/]\n\n'
            if status_id < 5:
                test_cases = '🤞🏻🤞🏻🤞🏻🤞🏻🤞🏻 [bold yellow]\
WAITING...[/] 🤞🏻🤞🏻🤞🏻🤞🏻🤞🏻‍'
            else:
                test_cases = ' '.join(t_results)
                test_cases += '\n'
            text += test_cases
            kattis_live.update(Align.center(text))
            if status_id > 5:
                kattis_live.stop()
                break
    if status_id == _ACCEPTED_STATUS:
        verdict = '👍🎆🔥🎈🎈 [bold yellow]YAY!! \
KEEP GOING...[/] 🎈🎈👍🎆🔥'
        console.print()
        config_data['accepted'] += 1
    else:
        verdict = '💪🧐💪 [bold green]SORRY![/] 🧐💪🧐'
    console.print(Align.center(verdict))
    config.update_problem_metadata(problemid, config_data)
    config_data = ui.show_problem_metadata(problemid)


def get_login_reply(cfg: configparser.ConfigParser) -> requests.Response:
    """Log in to Kattis.
    """
    console = Console()

    try:
        login_reply = login_from_config(cfg)
    except config.ConfigError as exc:
        console.print(exc)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        console.print('Login connection failed:', err)
        sys.exit(1)

    if not login_reply.status_code == 200:
        console.print('Login failed.')
        if login_reply.status_code == 403:
            console.print('Incorrect username or password/token (403)')
        elif login_reply.status_code == 404:
            console.print('Incorrect login URL (404)')
        else:
            console.print('Status code:', login_reply.status_code)
        sys.exit(1)
    return login_reply


def submit_solution(files: List[str], problemid: str,
                    language: str, mainclass: str,
                    tag: str, force: bool) -> None:
    """Submit a solution to Kattis.

    Args:
        files (Tuple[str]): Tuple of files to submit
        problem (str, optional): problemid. Defaults to ''.
        language (str, optional): language. Defaults to ''.
        mainclass (str, optional): main class/file. Defaults to ''.
        tag (str, optional): Tag. Defaults to ''.
        force (bool, optional): Force bumission without confirmation.
    """
    console = Console()
    try:
        cfg = config.get_kattisrc()
    except config.ConfigError as exc:
        console.print(exc)
        sys.exit(1)
    login_reply = get_login_reply(cfg)
    if not files:
        console.print('No files specified')
        sys.exit(1)

    files = sorted(list(set(files)))

    submit_url = get_url(cfg, 'submissionurl', 'submit')

    if not force:
        confirm_or_die(problemid, language, files, mainclass, tag)

    try:
        result = submit(submit_url,
                        login_reply.cookies,
                        problemid,
                        language,
                        files,
                        mainclass,
                        tag)
    except requests.exceptions.RequestException as err:
        console.print('Submit connection failed:', err, style='bold red')
        sys.exit(1)

    if result.status_code != 200:
        console.print('Submission failed.', style='bold red')
        if result.status_code == 403:
            console.print('Access denied (403)', style='bold red')
        elif result.status_code == 404:
            console.print('Incorrect submit URL (404)')
        else:
            console.print('Status code:', result.status_code, style='bold red')
        sys.exit(1)

    plain_result = result.content.decode('utf-8').replace('<br />', '\n')
    console.print(f'[bold blue]{plain_result}[/]')

    submission_url = None
    try:
        submission_url = get_submission_url(plain_result, cfg)
    except configparser.NoOptionError:
        pass

    if submission_url:
        show_kattis_judgement(problemid, submission_url, cfg)
