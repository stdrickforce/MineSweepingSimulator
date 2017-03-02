#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: stdrickforce (Tengyuan Fan)
# Email: <stdrickforce@gmail.com> <fantengyuan@baixing.com>

import logging
import logging.config
import random  # noqa
import time  # noqa

from vskfz import config
from vskfz.map import (  # noqa
    BoomException,
    WinException,
    Map,
)

logging.config.dictConfig(config.LOGGING_SETTINGS)
logger = logging.getLogger('main')


class Simulator(object):

    UNEXPLORED = '_'
    FLAGED = '#'
    MINE = '*'
    EXPLODED_MINE = 'X'

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

    def __init__(self, height, width, mine_count, stdout=True):
        self.map = Map(height, width, mine_count, stdout=stdout)
        self._map_last = [[self.UNEXPLORED] * width for i in range(height)]
        self._map_record = [[None] * width for i in range(height)]

        self._height = height
        self._width = width
        self._size = width * height
        self._sides = set()
        self._borders = set()
        self._wasteland = set()

        for i in range(self._height):
            for j in range(self._width):
                self._wasteland.add((i, j))

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

    def _add_to_sides(self, x, y):
        self._sides.add((x, y))
        for i, j in self._around(x, y):
            if self._map_last[i][j] == Map.UNEXPLORED:
                self._add_to_borders(i, j)
        self._remove_from_borders(x, y)
        self._remove_from_wasteland(x, y)

    def _add_to_borders(self, x, y):
        self._borders.add((x, y))
        self._remove_from_wasteland(x, y)

    def _remove_from_sides(self, x, y):
        if (x, y) in self._sides:
            self._sides.remove((x, y))

    def _remove_from_borders(self, x, y):
        if (x, y) in self._borders:
            self._borders.remove((x, y))

    def _remove_from_wasteland(self, x, y):
        if (x, y) in self._wasteland:
            self._wasteland.remove((x, y))

    def _calculate(self, x, y):
        uc, fc = 0, 0
        for i, j in self._around(x, y):
            if self._map_last[i][j] == Map.UNEXPLORED:
                uc += 1
            elif self._map_last[i][j] == Map.FLAGED:
                fc += 1
        self._map_record[x][y] = uc, fc

    def _collect_map(self):
        map_current = self.map.get_visible_map()
        for i in range(self._height):
            for j in range(self._width):
                # 地图若无变化，则不触发任何条件
                if map_current[i][j] == self._map_last[i][j]:
                    continue
                self._map_last[i][j] = map_current[i][j]
                if 0 < map_current[i][j] < 9:
                    self._add_to_sides(i, j)
                else:
                    self._remove_from_wasteland(i, j)

        # logger.info(self._sides)
        # logger.info(self._borders)
        # logger.info(self._wasteland)

        for i, j in self._sides:
            self._calculate(i, j)

    def _make_decision(self):

        res = []
        for i, j in self._sides:
            uc, fc = self._map_record[i][j]
            if uc == 0:
                continue
            # cell number equals to flaged count leads to no mines nearby.
            if self._map_last[i][j] == fc:
                for x, y in self._around(i, j):
                    if self._map_last[x][y] == Map.UNEXPLORED:
                        res.append((x, y, 'click'))
                self._remove_from_sides(i, j)
                return res

            # cell number euqlas to sum of flaged count and unexplored count
            # leads to all the nearby cells are mines
            elif self._map_last[i][j] - fc == uc:
                for x, y in self._around(i, j):
                    if self._map_last[x][y] == Map.UNEXPLORED:
                        res.append((x, y, 'right_click'))
                self._remove_from_sides(i, j)
                return res

        if self._wasteland:
            i, j = self._wasteland.pop()
        else:
            i, j = self._borders.pop()
        return [(i, j, 'click')]

    def run(self):
        try:
            self.map.click(1, 1)
            while True:
                self._collect_map()
                for x, y, operate in self._make_decision():
                    getattr(self.map, operate)(x, y)

        except BoomException:
            return False
        except WinException:
            return True


if __name__ == '__main__':
    height = 16
    width = 30
    mine_number = 99

    # s = Simulator(height, width, mine_number)
    # s.run()

    w, l = 0, 0
    for i in range(10000):
        logger.info(i)
        s = Simulator(height, width, mine_number, stdout=False)
        if s.run():
            w += 1
        else:
            l += 1
    print(w, l)


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
    s.start()
