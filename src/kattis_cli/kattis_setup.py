"""Setup helpers for Kattis CLI.

This module now exposes a :class:`SetupManager` which accepts a
``KattisClient`` in order to perform login flows. A module-level
``setup`` function delegates to a default manager to preserve the
original API used by the CLI.
"""

from pathlib import Path
import requests
from rich.console import Console
from rich.prompt import Prompt, Confirm
from typing import Optional, Any
from .client import KattisClient
from .utils import config

_LOGIN_URL = 'https://open.kattis.com/login'
_KATTISRCURL = "https://open.kattis.com/download/kattisrc"

# headers used to fetch kattisrc during interactive setup
_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) '
    'Ubuntu Chromium/83.0.4103.97 Chrome/83.0.4103.97 Safari/537.36'}
_HEADERS['Referer'] = _LOGIN_URL
_HEADERS['Content-Type'] = 'application/x-www-form-urlencoded'
_HEADERS['Origin'] = 'https://open.kattis.com'
_HEADERS['Host'] = 'open.kattis.com'
_HEADERS['Connection'] = 'keep-alive'
_HEADERS['Accept-Language'] = 'en-US,en;q=0.9'
_HEADERS['Accept-Encoding'] = 'gzip, deflate, br'
_HEADERS['Accept'] = (
    'text/html,application/xhtml+xml,application/xml;q=0.9,'
    'image/webp,*/*;q=0.8'
)

_KATTISRC = Path.home().joinpath(".kattisrc")


class SetupManager:
    """Interactive setup manager for installing .kattisrc.

    The manager accepts a `KattisClient` instance so the underlying
    authentication logic can be injected (useful for testing).
    """

    def __init__(self, client: Optional[KattisClient] = None) -> None:
        self.client = client or KattisClient()

<<<<<<< Updated upstream
=======
    @staticmethod
    def _is_valid_kattisrc(content: str) -> bool:
        """Return True when downloaded text looks like a .kattisrc file."""
        parser = configparser.ConfigParser()
        try:
            parser.read_string(content)
        except configparser.Error:
            return False
        if not parser.has_section('user') or not parser.has_section('kattis'):
            return False
        if not parser.has_option('user', 'username'):
            return False
        has_secret = (
            parser.has_option('user', 'token') or parser.has_option(
                'user', 'password')
        )
        return has_secret and parser.has_option('kattis', 'hostname')

    def _download_kattisrc(
            self,
            cookies: requests.cookies.RequestsCookieJar,
            username: str = '',
            password: str = '',
    ) -> Optional[Any | str]:
        """Download and validate kattisrc using cookies or a fresh session."""
        header_candidates = [
            getattr(self.client, '_HEADERS', {}),
            _HEADERS,
        ]
        for headers in header_candidates:
            try:
                res = requests.get(
                    _KATTISRCURL,
                    cookies=cookies,
                    headers=headers,
                    timeout=10,
                )
            except requests.RequestException:
                continue
            if (res.status_code == 200) and \
                    (self._is_valid_kattisrc(res.text)):
                return res.text

        # Fallback: build a fresh authenticated web session and retry.
        if username and password:
            try:
                with requests.Session() as session:
                    session.post(
                        _LOGIN_URL,
                        data={'user': username, 'password': password},
                        headers=_HEADERS,
                        timeout=10,
                    )
                    res = session.get(
                        _KATTISRCURL,
                        headers=_HEADERS,
                        timeout=10,
                    )
                if res.status_code == 200 and \
                        self._is_valid_kattisrc(res.text):
                    return res.text
            except requests.RequestException:
                pass
        return None

>>>>>>> Stashed changes
    def check_kattisrc(self) -> bool:
        """Check if kattisrc file exists and is valid.

        Returns:
            bool: True if kattisrc is valid, False otherwise.
        """
        try:
            cfg = config.get_kattisrc()
            response = self.client.login_from_config(cfg)
            if response.status_code != 200:
                return False
        except config.ConfigError:
            return False
        return True

    def setup(self) -> None:
        """Run the interactive setup for Kattis CLI.
        """
        console = Console()
        console.print(":cat: Welcome to Kattis CLI! :cat:", style="bold blue")
        if self.check_kattisrc():
            console.print(
                ":rocket: [bold blue]kattisrc already exists with valid "
                "token.[/]"
            )
            console.print(
                ":rocket: [bold green]You are ready to use Kattis CLI.[/]"
            )
            return
        console.print("You need your Kattis credentials for this setup.")
        if Confirm.ask("Do you have an account on Kattis?", default=True):
            while True:
                username = Prompt.ask(
                    "Please enter your username or email", password=False)
                while True:
                    password = Prompt.ask(
                        "Please enter your password", password=True)
                    if Confirm.ask(
                        "Want to see your password? ",
                            default=False):
                        console.print(f"You entered: {password}")
                        if Confirm.ask("Is this correct? ", default=True):
                            console.print(":rocket: Logging in...")
                            break
                    else:
                        console.print(":rocket: Logging in...")
                        break

                response = self.client.login(_LOGIN_URL, username, password)
                if response.status_code == 200:
                    console.print(":rocket: Login successful!")
                    res = requests.get(
                        _KATTISRCURL,
                        cookies=response.cookies,
                        headers=_HEADERS,
                        timeout=10,
                    )
                    if res.status_code == 200:
                        with open(_KATTISRC, "w", encoding='utf-8') as f:
                            f.write(res.text)
                        console.print(
                            f":rocket: kattisrc downloaded and saved to "
                            f"{str(_KATTISRC)}"
                        )
                    else:
                        text = (
                            ":loudly_crying_face:\n"
                            "kattisrc download failed. Please download "
                            "kattisrc manually from:\n"
                            "https://open.kattis.com/download/kattisrc\n"
                            "and save it to your system's home directory with "
                            "the name .kattisrc\n"
                        )
                        console.print(text)
                        break
                else:
                    console.print(
                        ":loudly_crying_face:\n"
                        "Login failed. Please try again."
                    )
        else:
            console.print("Please register your account at: ")
            console.print(
                "[link=\"https://open.kattis.com/register\"]"
                "https://open.kattis.com/register[/link]"
            )
            console.print("and try again.")


# Default manager for compatibility
_manager = SetupManager()


def check_kattisrc() -> bool:
    """Check if kattisrc file exists and is valid.

    Returns:
        bool: True if kattisrc is valid, False otherwise.
    """
    return _manager.check_kattisrc()


def setup() -> None:
    """Wrapper for Katti-cli setup
    """
    return _manager.setup()
