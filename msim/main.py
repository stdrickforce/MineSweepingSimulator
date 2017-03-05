#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: stdrickforce (Tengyuan Fan)
# Email: <stdrickforce@gmail.com> <fantengyuan@baixing.com>

import logging
import logging.config
import random  # noqa
import time  # noqa

from msim import config
from msim.map import (  # noqa
    BoomException,
    WinException,
    Map,
)

logging.config.dictConfig(config.LOGGING_SETTINGS)
logger = logging.getLogger('main')


class Simulator(object):

    SENTENCES = [
        "Not difficult to me.",
        "It's too easy to me.",
        "Do you have anything harder?",
        "I can go anywhere.",
        "It will soon be soluted.",
        "Mines are history.",
        "Let's see who's tougher.",
        "Sapper reporting.",
        "Big job, huh?",
    ]

    def __init__(self, height=9, width=9, mine_count=10, stdout=True):
        self.map = Map(height, width, mine_count, stdout=stdout)

        self._height = height
        self._width = width
        self._mine_count = mine_count
        self._flag_count = 0
        self._size = width * height

    def _around(self, x, y):
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if i == 0 and j == 0:
                    continue
                if x + i < 0 or x + i >= self._height:
                    continue
                if y + j < 0 or y + j >= self._width:
                    continue
                yield x + i, y + j

    def _calculate(self, x, y):
        uc, fc = 0, 0
        mc = self._map[x][y]
        for i, j in self._around(x, y):
            if self._map[i][j] == Map.UNEXPLORED:
                uc += 1
            elif self._map[i][j] == Map.FLAG:
                fc += 1
                mc -= 1
        return uc, fc, mc

    def _graph(self):
        self._map = self.map.get_visible_map()

        explored = set()
        sides = set()
        borders = set()

        def _explore(i, j):
            if (i, j) in explored:
                return
            if self._map[i][j] != Map.UNEXPLORED:
                return

            s = [(i, j)]
            while s:
                i, j = s.pop()
                explored.add((i, j))
                for x, y in self._around(i, j):
                    if self._map[x][y] == Map.UNEXPLORED:
                        if (x, y) not in explored:
                            s.append((x, y))
                    elif isinstance(self._map[x][y], int):
                        sides.add((x, y))
                        borders.add((i, j))

        for i in range(self._height):
            for j in range(self._width):
                _explore(i, j)

        return list(sides), list(borders), explored - borders

    def _search(self, x, y):

        votes = {}

        def _try(mark):

            c, s = 0, []

            def _mark(x, y, mark):
                self._map[x][y] = mark
                s.append((x, y, mark))
            _mark(x, y, mark)

            def _clear(s):
                for a, b, mark in s:
                    self._map[a][b] = Map.UNEXPLORED

            while c < len(s):
                a, b, mark = s[c]
                for i, j in self._around(a, b):
                    if not isinstance(self._map[i][j], int):
                        continue
                    uc, fc, mc = self._calculate(i, j)
                    if mc < 0 or uc < mc:
                        _clear(s)
                        return False
                    elif uc == mc:
                        for p, q in self._around(i, j):
                            if self._map[p][q] == Map.UNEXPLORED:
                                _mark(p, q, Map.FLAG)
                    elif mc == 0:
                        for p, q in self._around(i, j):
                            if self._map[p][q] == Map.UNEXPLORED:
                                _mark(p, q, Map.SAFE)
                c += 1

            for a, b, mark in s:
                key = (a, b)
                votes.setdefault(key, 0)
                if mark == Map.SAFE:
                    votes[key] += 1
                elif mark == Map.FLAG:
                    votes[key] += 3
                self._map[a][b] = Map.UNEXPLORED
            return True

        if not _try(Map.FLAG):
            yield x, y, 'click'
            return
        if not _try(Map.SAFE):
            yield x, y, 'right_click'
            return

        for k, v in votes.items():
            if v == 2:
                yield k[0], k[1], 'click'
            elif v == 6:
                yield k[0], k[1], 'right_click'

    def _make_decision(self):

        decisions = {}

        sides, borders, wastelands = self._graph()

        for i, j in sides:
            uc, fc, mc = self._calculate(i, j)
            if mc == 0:
                decisions[(i, j)] = 'double_click'
            elif uc == mc:
                for x, y in self._around(i, j):
                    if self._map[x][y] == Map.UNEXPLORED:
                        decisions[(x, y)] = 'right_click'
        if decisions:
            return decisions

        for i, j in borders:
            for x, y, operate in self._search(i, j):
                return {(x, y): operate}

        corner, edge, inside = [], [], []
        for i, j in wastelands:
            p = i in [0, self._height - 1]
            q = j in [0, self._width - 1]
            if p and q:
                corner.append((i, j))
            elif p or q:
                edge.append((i, j))
            else:
                inside.append((i, j))

        if corner:
            return {random.choice(corner): 'click'}
        elif edge:
            return {random.choice(edge): 'click'}
        elif inside:
            return {random.choice(inside): 'click'}
        else:
            return {random.choice(borders): 'click'}

    def run(self):
        try:
            self.map.click(
                int(self._height / 2),
                int(self._width / 2)
            )
            while True:
                for p, operate in self._make_decision().items():
                    # logger.info('%s: %s, %s' % (operate, p[0], p[1]))
                    getattr(self.map, operate)(*p)
        except BoomException:
            return False
        except WinException:
            return True


if __name__ == '__main__':

    height = 16
    width = 30
    mine_number = 99

    s = Simulator(height, width, mine_number)
    s.run()

    # w, l = 0, 0
    # for i in range(10000):
    #     logger.info(i)
    #     s = Simulator(height, width, mine_number, stdout=True)
    #     if s.run():
    #         w += 1
    #     else:
    #         l += 1
    # print(w, l)


def simulate():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("height")
    parser.add_argument("width")
    parser.add_argument("mine_number")
    args = parser.parse_args()

    height = int(args.height)
    width = int(args.width)
    mine_number = int(args.mine_number)

    s = Simulator(height, width, mine_number)
    s.run()
