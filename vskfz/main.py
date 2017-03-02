#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: stdrickforce (Tengyuan Fan)
# Email: <stdrickforce@gmail.com> <fantengyuan@baixing.com>

import functools
import logging
import logging.config
import random
import time
import os

from vskfz import config

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

    def __init__(self, height, width, mine_count):
        logger.info('a new game')
        if mine_count > height * width - 1:
            raise Exception('no enough space to place mine')
        self._height = height
        self._width = width
        self._size = height * width
        self._mine_count = mine_count

    def _refresh_map(func):

        @functools.wraps(func)
        def wraps(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            finally:
                time.sleep(0.05)
                self._print_map()
        return wraps

    def _print_map(self):
        os.system('clear')
        for i in range(self._height):
            s = ''
            for j in range(self._width):
                s += '%s ' % self._map[i][j]
            print(s)
        self.change_mind()
        print(self._lastword[1])

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
        '''
        calculate mine numbers around a cell.
        '''
        count = 0
        unexplored_count = 0
        flaged_count = 0
        for i, j in self._around(x, y):
            if (i, j) in self._mines:
                count += 1
            if self._map[i][j] == self.UNEXPLORED:
                unexplored_count += 1
            elif self._map[i][j] == self.FLAGED:
                flaged_count += 1
        self._record_map[x][y] = unexplored_count, flaged_count
        return count

    @_refresh_map
    def _extend(self, x, y):

        s = [(x, y)]
        while s:
            i, j = s.pop()
            self._map[i][j] = self._calculate(i, j)
            if self._map[i][j] != 0 and self._record_map[i][j][0] > 0:
                self._sides.add((i, j))
                continue
            for p, q in self._around(i, j):
                if self._map[p][q] == self.UNEXPLORED:
                    s.append((p, q))

    def initMap(self):
        self._steps = 0
        self._mines = set()
        self._sides = set()
        self._flags = 0
        self._map = []
        self._record_map = []
        self._lastword = (0, '')

        for i in range(self._height):
            self._map.append([self.UNEXPLORED] * self._width)
            self._record_map.append([None] * self._width)
        self._print_map()

        ps = random.sample(range(self._size), self._mine_count + 1)

        def parse(p):
            return p / self._width, p % self._width

        # Take the first step
        x, y = parse(ps[0])
        self._map[x][y] = 0

        # Init mines in the map
        for i in ps[1:]:
            p, q = parse(i)
            self._mines.add((p, q))

        self._extend(x, y)

    @_refresh_map
    def boom(self, x, y):
        for i, j in self._mines:
            self._map[i][j] = self.MINE
        self._map[x][y] = self.EXPLODED_MINE
        self.change_mind("Sorry for losing the game.")
        return False

    @_refresh_map
    def win(self):
        self.change_mind("It's your dime")
        return False

    def change_mind(self, message=None, force=False):
        if message:
            self._lastword = (time.time(), message)
        elif force or time.time() - self._lastword[0] > 3:
            message = random.choice(self.SENTENCES)
            self._lastword = (time.time(), message)

    @_refresh_map
    def waiting(self):
        # time.sleep(1)
        print("Not what I had in mind...")
        self.change_mind()
        # time.sleep(2)

    @_refresh_map
    def step(self):

        for i, j in self._sides:

            self._calculate(i, j)
            unexplored_count, flaged_count = self._record_map[i][j]

            # extend all unexplored neighbours
            if flaged_count == self._map[i][j]:
                for x, y in self._around(i, j):
                    if self._map[x][y] == self.UNEXPLORED:
                        self._extend(x, y)
                self._sides.remove((i, j))
                return True
            # mark all unexplored neighbours as mine.
            elif unexplored_count + flaged_count == self._map[i][j]:
                for x, y in self._around(i, j):
                    if self._map[x][y] == self.UNEXPLORED:
                        self._map[x][y] = self.FLAGED
                        self._flags += 1
                self._sides.remove((i, j))
                return True

        def calculate_mine_probability(i, j):
            res = 1.0
            for p, q in self._around(i, j):
                if 0 < self._map[p][q] < 9:
                    unexplored, flaged = self._record_map[p][q]
                    pr = float(self._map[p][q] - flaged) / unexplored
                    res = min(res, pr)
            return res

        min_pr, candidates, count, wasteland = 1.0, [], 0, []
        for i in range(self._height):
            for j in range(self._width):
                if self._map[i][j] != self.UNEXPLORED:
                    continue
                count += 1

                pr = calculate_mine_probability(i, j)
                if pr == 1.0:
                    wasteland.append((i, j))
                elif abs(pr - min_pr) < 0.0001:
                    candidates.append((i, j))
                elif pr < min_pr:
                    min_pr = pr
                    candidates = [(i, j)]

        mine_remain = len(self._mines) - self._flags
        logger.info('border pr: %s' % min_pr)
        if count and float(mine_remain) / count < min_pr:
            logger.info('wasteland pr: %s' % (float(mine_remain) / count))
            candidates = wasteland

        if not candidates:
            return self.win()
        self.waiting()

        x, y = random.choice(candidates)
        if (x, y) in self._mines:
            return self.boom(x, y)
        else:
            self._extend(x, y)
        return True

    def start(self):
        self.initMap()
        while self.step():
            pass


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
