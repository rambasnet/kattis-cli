#! /usr/bin/env python3
from sys import stdin
lines = stdin.readlines()
for line in lines[1:]:
    points = [int(i) for i in line.split()]
    j = 2
    i = 1
    # area = 1/2[(x1y2+x2y3+...xny1) - (y1x2+y2x3+y3x4..ynx1)]
    # print(points)
    exp1 = 0
    exp2 = 0
    while i < 2 * points[0] - 2:
        exp1 += points[i] * points[i + 3]
        i += 2
        exp2 += points[j] * points[j + 1]
        j += 2

    exp1 += points[-2] * points[2]
    exp2 += points[-1] * points[1]
    # print(exp1, exp2)
    print('{0:g}'.format((exp1 - exp2) / 2))
