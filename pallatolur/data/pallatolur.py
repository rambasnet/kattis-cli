#! /usr/bin/env python3

import sys


def solve():  # type: ignore
    """"""
    a = int(sys.stdin.readline())
    b = int(sys.stdin.readline())
    if a < 2 and b >= 2:
        print('1\n2')
    else:
        print(':(')


if __name__ == '__main__':
    solve()  # type: ignore
