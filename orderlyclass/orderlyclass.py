#! /usr/bin/env python3

import sys


def flip_compare(str1, str2, i, j):
    rest = j + 1
    match = False
    while i < rest:
        # print(str1[i], str2[j], file=sys.stderr)
        if str1[i] != str2[j]:
            match = False
            break
        i += 1
        j -= 1
    else:
        match = True
    if not match:
        return 0
    for k in range(rest, len(str1)):
        if str1[k] != str2[k]:
            match = False
            break
    if match:
        return 1
    else:
        return 0


def solve():
    str1 = sys.stdin.readline().strip()
    str2 = sys.stdin.readline().strip()
    # "ab" : "ba" -> 1
    # "abc" : "cba" -> 1
    # "abc" : "bca" -> 0
    # "abc" : "bac" -> 1
    # "abc" : "cab" -> 0
    # "abc" : "acb" -> 1
    count = 0
    previous_match = True
    i = 0
    while i < len(str1) and previous_match:
        if str1[i] != str2[i]:
            previous_match = False
        for j in range(i + 1, len(str1)):
            count += flip_compare(str1, str2, i, j)
            # print(i, j, count, file=sys.stderr)
        i += 1
    print(count)


if __name__ == '__main__':
    solve()
