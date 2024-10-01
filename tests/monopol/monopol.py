#! /usr//bin/env python

import sys
from collections import defaultdict
from typing import DefaultDict


def find_prob() -> DefaultDict:
    """_summary_

    Returns:
        DefaultDict: _description_
    """
    ways: DefaultDict = defaultdict(int)
    for i in range(1, 7):
        for j in range(1, 7):
            ways[i + j] += 1
    return ways


def solve() -> None:
    """Main function to solve the problem.
    """
    N = int(sys.stdin.readline())
    nums = map(int, sys.stdin.readline().split())
    ways = find_prob()
    ans = 0
    for n in nums:
        ans += ways[n] / 36
    print(ans)


if __name__ == "__main__":
    solve()
