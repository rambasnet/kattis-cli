#!/usr/bin/env python3
"""Headless fireworks animation for CI/Docker.

This script intentionally avoids any GUI libraries and provides a
terminal-only fireworks animation suitable for headless environments.
Configuration can be provided via `scripts/ui_config.yml`
"""

import os
import sys
import locale
import time
from random import randint, choice


def run_fireworks() -> None:
    """Simple ASCII fireworks for headless environments.

    Draws random bursts in the terminal using ANSI colors. Works in CI/Docker
    and avoids external dependencies.
    """
    frames = 5
    width = 60
    height = 20
    symbols = ['*', '•', '✶', '✸']
    colors = [
        '\x1b[37m',  # white
        '\x1b[31m',  # red
        '\x1b[32m',  # green
        '\x1b[34m',  # blue
        '\x1b[33m',  # yellow
        '\x1b[35m',  # magenta
        '\x1b[36m',  # cyan
    ]
    reset = '\x1b[0m'

    # Only emit ANSI color codes when stdout is a TTY and terminal
    # appears to support colors. In CI or when output is captured the
    # escape characters may be shown literally (e.g. as ``\u001b[...]``)
    # so we disable color codes in that case to avoid escaped sequences
    # appearing in logs.
    use_color = sys.stdout.isatty() and os.environ.get('NO_COLOR') is None
    if os.environ.get('TERM') == 'dumb':
        use_color = False
    if not use_color:
        colors = ['']
        reset = ''

    # Detect Unicode support in the execution environment. Some minimal
    # container images or redirected outputs use an ASCII locale so fancy
    # symbols (✶, ✸, •, emojis) render poorly or get replaced. We fall
    # back to ASCII symbols when Unicode is not supported.
    out_encoding = sys.stdout.encoding or \
        locale.getpreferredencoding(False) or ''
    out_encoding = (out_encoding or '').lower()
    supports_unicode = ('utf' in out_encoding)
    if not supports_unicode:
        # Simple ASCII fallback symbols
        symbols = ['*', '+', 'o', '.']
        # Replace message with ASCII-only fallback if necessary
        # Inform interactive users why we fell back (but avoid noisy logs
        # in captured/non-interactive runs).
        if sys.stdout.isatty():
            print(
                'Note: terminal does not appear to support UTF-8 — '
                'using ASCII fallback for fireworks.',
                file=sys.stderr,
            )

    try:
        # Hide cursor (only when terminal supports it)
        if use_color:
            sys.stdout.write('\x1b[?25l')
        for _ in range(frames):
            # clear screen when supported, otherwise don't emit escapes
            if use_color:
                sys.stdout.write('\x1b[2J\x1b[H')
            cx = randint(width // 4, 3 * width // 4)
            cy = randint(height // 4, 3 * height // 4)
            grid = [[' ' for _ in range(width)] for _ in range(height)]
            # place particles
            for _ in range(randint(12, 40)):
                dx = int(randint(-8, 8) * (randint(0, 100) / 100.0))
                dy = int(randint(-4, 4) * (randint(0, 100) / 100.0))
                x = max(0, min(width - 1, cx + dx))
                y = max(0, min(height - 1, cy + dy))
                grid[y][x] = choice(symbols)

            # render
            for row in grid:
                line = ''
                for ch in row:
                    if ch == ' ':
                        line += ' '
                    else:
                        line += choice(colors) + ch + reset
                sys.stdout.write(line + '\n')
            sys.stdout.flush()
            time.sleep(0.12)

        # final message
        msg = '🎉 Congratulations — Accepted! 🎉'
        sys.stdout.write('\n')
        if use_color:
            sys.stdout.write('\x1b[1;33m')
            sys.stdout.write(msg)
            sys.stdout.write('\x1b[0m\n')
        else:
            sys.stdout.write(msg + '\n')
        sys.stdout.flush()
    finally:
        # show cursor again
        if use_color:
            sys.stdout.write('\x1b[?25h')
        sys.stdout.flush()


if __name__ == '__main__':
    run_fireworks()
