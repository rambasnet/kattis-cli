"""Testing subprocess.
"""

import selectors
import subprocess


def test_output():
    """Testing program output.
    """
    p = subprocess.Popen(["python", "./tests/random_out.py"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sel = selectors.DefaultSelector()
    sel.register(p.stdout, selectors.EVENT_READ)  # type: ignore
    sel.register(p.stderr, selectors.EVENT_READ)  # type: ignore
    ans = ''
    error = ''
    done = False
    while not done:
        for key, _ in sel.select():
            data = key.fileobj.read1().decode()  # type: ignore
            if not data:
                done = True
                break
            if key.fileobj is p.stdout:
                # print(data, end="")
                ans = data
            else:
                # print(data, end="", file=sys.stderr)
                error = data
    assert ans == 'Hello, world!\n'
    assert error == 'Error\n'
    # print('All tests passed!')


def test_program_error():
    """Testing program error.
    """
    p = subprocess.Popen(["python", "random_out1.py"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sel = selectors.DefaultSelector()
    sel.register(p.stdout, selectors.EVENT_READ)  # type: ignore
    sel.register(p.stderr, selectors.EVENT_READ)  # type: ignore
    ans = ''
    error = ''
    done = False
    while not done:
        for key, _ in sel.select():
            data = key.fileobj.read1().decode()  # type: ignore
            if not data:
                done = True
                break
            if key.fileobj is p.stdout:
                # print(data, end="")
                ans = data
            else:
                # print(data, end="", file=sys.stderr)
                error = data
    assert ans == ''
    assert error.startswith("python: can't open file")


def test_syntax_error():
    """Testing syntax error.
    """
    p = subprocess.Popen(["python", "./tests/syntax_error.py"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sel = selectors.DefaultSelector()
    sel.register(p.stdout, selectors.EVENT_READ)  # type: ignore
    sel.register(p.stderr, selectors.EVENT_READ)  # type: ignore
    ans = ''
    error = ''
    done = False
    while not done:
        for key, _ in sel.select():
            data = key.fileobj.read1().decode()  # type: ignore
            if not data:
                done = True
                break
            if key.fileobj is p.stdout:
                # print(data, end="")
                ans = data
            else:
                # print(data, end="", file=sys.stderr)
                error = data

    assert 'SyntaxError: ' in error
    assert ans == ''
