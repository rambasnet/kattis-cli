#!/usr/bin/env python
"""
Object-oriented Kattis API client.

This class wraps login, submit and status-checking functionality previously
implemented as module-level functions in `kattis.py`.
"""
from typing import List, Any
import sys
import os
import re
import time
import configparser
from bs4 import BeautifulSoup
import requests
import requests.exceptions
import requests.cookies
from rich.console import Console
from rich.align import Align
from rich.live import Live
from rich.prompt import Confirm

from kattis_cli.utils import languages
from kattis_cli.utils import config
from kattis_cli import ui


class KattisClient:
    """A simple client for interacting with Kattis (login, submit, poll)."""

    _HEADERS = {'User-Agent': 'kattis-cli-submit'}

    _RUNNING_STATUS = 5
    _COMPILE_ERROR_STATUS = 8
    _ACCEPTED_STATUS = 16

    _STATUS_MAP = {
        0: 'New',
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
        _ACCEPTED_STATUS: 'Accepted',
    }

    def __init__(self) -> None:
        self.console = Console()

    # --- Authentication ---
    def login(self, login_url: str, username: str,
              password: str = '', token: str = '') -> requests.Response:
        """Log in to Kattis. At least one of password or token is required."""
        login_args = {'user': username, 'script': 'true'}
        if password:
            login_args['password'] = password
        if token:
            login_args['token'] = token

        return requests.post(
            login_url,
            data=login_args,
            headers=self._HEADERS,
            timeout=10)

    def login_from_config(self, cfg: configparser.ConfigParser) -> requests.Response:
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

        loginurl = self.get_url(cfg, 'loginurl', 'login')
        return self.login(loginurl, username, password, token)

    def get_url(self, cfg: configparser.ConfigParser, option: str, default: str) -> str:
        if cfg.has_option('kattis', option):
            return cfg.get('kattis', option)
        else:
            return f"https://{cfg.get('kattis', 'hostname')}/{default}"

    # --- Submission ---
    def submit(self,
               submit_url: str,
               cookies: requests.cookies.RequestsCookieJar,
               problem: str,
               language: str,
               files: List[str],
               mainclass: str,
               tag: str) -> requests.Response:
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
            headers=self._HEADERS, timeout=10)

    def get_submission_url(self, submit_response: str,
                           cfg: configparser.ConfigParser) -> str:
        m = re.search(r'Submission ID: (\d+)', submit_response)
        if m:
            submissions_url = self.get_url(
                cfg, 'submissionsurl', 'submissions')
            submission_id = m.group(1)
            return f'{submissions_url}/{submission_id}'
        else:
            raise config.ConfigError(
                'Could not find submission ID in response')

    def get_submission_status(self,
                              submission_url: str,
                              cookies: requests.cookies.RequestsCookieJar) -> Any:
        reply = requests.get(
            submission_url + '?json',
            cookies=cookies,
            headers=self._HEADERS, timeout=10)
        return reply.json()

    # --- HTML parsing ---
    def parse_row_html(self, html: str) -> Any:
        runtime = '❓ s'
        status = '❓'
        language = '❓'
        test_status = '❓/❓'
        soup = BeautifulSoup(html, 'html.parser')
        tr_submission: Any = soup.find("tr", {"data-submission-id": True})
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
            if 'Accepted' in title[-1]:
                test_result.append(f'{num}✅')
            elif 'not checked' in title[-1]:
                test_result.append(f'{num}❓')
            else:
                test_result.append(f'{num}❌')
        return runtime, status, language, test_status, test_result

    # --- High level flows ---
    def show_kattis_judgement(self, problemid: str, submission_url: str,
                              cfg: configparser.ConfigParser) -> None:
        config_data = ui.show_problem_metadata(problemid)
        config_data['submissions'] += 1
        console = Console()
        login_reply = self.login_from_config(cfg)
        title = '\n[bold blue]                           '
        title += ':cat: Kattis Judgement Results :cat:[/]\n'
        status_id = 0
        with Live(console=console, screen=False,
                  refresh_per_second=10) as kattis_live:

            while True:
                time.sleep(0.1)
                result = self.get_submission_status(submission_url,
                                                    login_reply.cookies)
                rt, status, lang, t_status, t_results = self.parse_row_html(
                    result['row_html'])
                status_id = int(result['status_id'])
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
                    test_cases = '🤞🏻🤞🏻🤞🏻🤞🏻🤞🏻 [bold yellow]WAITING...[/] 🤞🏻🤞🏻🤞🏻🤞🏻🤞🏻‍'
                else:
                    test_cases = ' '.join(t_results)
                    test_cases += '\n'
                text += test_cases
                kattis_live.update(Align.center(text))
                if status_id > 5:
                    kattis_live.stop()
                    break
        if status_id == self._ACCEPTED_STATUS:
            verdict = '👍🎆🔥🎈🎈 [bold yellow]YAY!! KEEP GOING...[/] 🎈🎈👍🎆🔥'
            console.print()
            config_data['accepted'] += 1
        else:
            verdict = '💪🧐💪 [bold green]SORRY![/] 🧐💪🧐'
        console.print(Align.center(verdict))
        config.update_problem_metadata(problemid, config_data)
        ui.show_problem_metadata(problemid)

    def get_login_reply(self, cfg: configparser.ConfigParser) -> requests.Response:
        try:
            login_reply = self.login_from_config(cfg)
        except config.ConfigError as exc:
            self.console.print(exc)
            sys.exit(1)
        except requests.exceptions.RequestException as err:
            self.console.print('Login connection failed:', err)
            sys.exit(1)

        if not login_reply.status_code == 200:
            self.console.print('Login failed.')
            if login_reply.status_code == 403:
                self.console.print(
                    'Incorrect username or password/token (403)')
            elif login_reply.status_code == 404:
                self.console.print('Incorrect login URL (404)')
            else:
                self.console.print('Status code:', login_reply.status_code)
            sys.exit(1)
        return login_reply

    def submit_solution(self, files: List[str], problemid: str,
                        language: str, mainclass: str,
                        tag: str, force: bool) -> None:
        try:
            cfg = config.get_kattisrc()
        except config.ConfigError as exc:
            self.console.print(exc)
            sys.exit(1)
        login_reply = self.get_login_reply(cfg)
        if not files:
            self.console.print('No files specified')
            sys.exit(1)

        files = sorted(list(set(files)))

        submit_url = self.get_url(cfg, 'submissionurl', 'submit')

        if not force:
            # reuse module-level confirm UI
            self._confirm_or_die(problemid, language, files, mainclass, tag)

        try:
            result = self.submit(submit_url,
                                 login_reply.cookies,
                                 problemid,
                                 language,
                                 files,
                                 mainclass,
                                 tag)
        except requests.exceptions.RequestException as err:
            self.console.print('Submit connection failed:',
                               err, style='bold red')
            sys.exit(1)

        if result.status_code != 200:
            self.console.print('Submission failed.', style='bold red')
            if result.status_code == 403:
                self.console.print('Access denied (403)', style='bold red')
            elif result.status_code == 404:
                self.console.print('Incorrect submit URL (404)')
            else:
                self.console.print(
                    'Status code:', result.status_code, style='bold red')
            sys.exit(1)

        plain_result = result.content.decode('utf-8').replace('<br />', '\n')
        self.console.print(f'[bold blue]{plain_result}[/]')

        submission_url = None
        try:
            submission_url = self.get_submission_url(plain_result, cfg)
        except configparser.NoOptionError:
            pass

        if submission_url:
            self.show_kattis_judgement(problemid, submission_url, cfg)

    def _confirm_or_die(self, problem: str, language: str,
                        files: List[str], mainclass: str,
                        tag: str) -> None:
        console = Console()
        console.clear()
        console.print('Problem:', problem)
        console.print('Language:', language)
        console.print('Files:', ', '.join(files))
        if mainclass:
            if language in languages.GUESS_MAINFILE:
                console.print('Main file:', mainclass)
            else:
                console.print('Mainclass:', mainclass)
        if tag:
            console.print('Tag:', tag)
        if not Confirm.ask('Submit to Kattis', default=True):
            console.print('Cancelling...')
            sys.exit(1)
