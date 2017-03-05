#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: stdrickforce (Tengyuan Fan)
# Email: <stdrickforce@gmail.com> <fantengyuan@baixing.com>

import functools
import logging
import logging.config
import random
import time  # noqa
import os

from msim import config

logging.config.dictConfig(config.LOGGING_SETTINGS)
logger = logging.getLogger('main')


class BoomException:
    pass


class WinException:
    pass


class Map(object):

    UNEXPLORED = '_'
    FLAGED = '#'
    MINE = '*'
    EXPLODED_MINE = 'X'

    def __init__(self, height, width, mine_count, stdout=True):
        logger.info('a new map generated')
        if mine_count > height * width - 1:
            raise Exception('no enough space to place mine')
        self._height = height
        self._width = width
        self._mine_count = mine_count
        self._mines = set()
        self._need_explored = set()
        self._size = height * width
        self._real_mine_count = 0
        self._initialized = False
        self._stdout = stdout

        self._map = []
        self._map_visible = []
        for i in range(self._height):
            self._map.append([0] * self._width)
            self._map_visible.append([self.UNEXPLORED] * self._width)
        for i in range(self._size):
            self._need_explored.add(i)
        self._print_map()

    def _print_map(self):
        if not self._stdout:
            return
        os.system('clear')
        for i in range(self._height):
            s = ''
            for j in range(self._width):
                s += '%s ' % self._map_visible[i][j]
            print(s)

    def _refresh_map(func):
        @functools.wraps(func)
        def wraps(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            finally:
                self._print_map()
        return wraps

    @_refresh_map
    def click(self, x, y):
        if not self._initialized:
            self._initialized = True
            self._initMap(x, y)
            self._extend(x, y)
        elif self._map[x][y] == self.MINE:
            self._boom(x, y)
        elif self._map_visible[x][y] == self.UNEXPLORED:
            self._extend(x, y)
        if not self._need_explored:
            self._win()

    @_refresh_map
    def right_click(self, x, y):
        '''
        mark a cell with flag
        '''
        if self._map_visible[x][y] == self.FLAGED:
            self._setVisible(x, y, self.UNEXPLORED)
        elif self._map_visible[x][y] == self.UNEXPLORED:
            self._setVisible(x, y, self.FLAGED)

    def get_visible_map(self):
        return self._map_visible

    def _boom(self, x, y):
        for i in range(self._height):
            for j in range(self._width):
                if self._map[i][j] == self.MINE:
                    self._setVisible(i, j, self.MINE)
        self._setVisible(x, y, self.EXPLODED_MINE)
        raise BoomException()

    def _win(self):
        for i in range(self._height):
            for j in range(self._width):
                if self._map[i][j] == self.MINE:
                    self._setVisible(i, j, self.FLAGED)
        raise WinException()

    def _setMine(self, x, y):
        '''
        setup a mine at (i, j) cell
        '''
        if self._real_mine_count >= self._mine_count:
            return
        self._map[x][y] = self.MINE
        for i, j in self._around(x, y):
            if self._map[i][j] == self.MINE:
                continue
            self._map[i][j] += 1
        self._mines.add((x, y))
        pos = x * self._width + y
        self._need_explored.remove(pos)
        self._real_mine_count += 1

    def _setVisible(self, x, y, c):
        self._map_visible[x][y] = c

    def _initMap(self, x, y):
        '''
        initialize map, cell(x, y) should not coutain a mine.
        '''
        ps = random.sample(range(self._size), self._mine_count + 1)
        for p in ps:
            i = p / self._width
            j = p % self._width
            if i == x and j == y:
                continue
            self._setMine(i, j)

    def _around(self, x, y):
        '''
        iterate nearby cells of (x, y).
        '''
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if i == 0 and j == 0:
                    continue
                if x + i < 0 or x + i >= self._height:
                    continue
                if y + j < 0 or y + j >= self._width:
                    continue
                yield x + i, y + j

    def _extend(self, x, y):
        s = [(x, y)]
        while s:
            i, j = s.pop()
            pos = i * self._width + j
            if pos in self._need_explored:
                self._need_explored.remove(pos)
            self._setVisible(i, j, self._map[i][j])
            if self._map[i][j] != 0:
                continue
            for p, q in self._around(i, j):
                if self._map_visible[p][q] == self.UNEXPLORED:
                    s.append((p, q))


if __name__ == '__main__':
    h = 10
    w = 10
    m = Map(h, w, 10)
    for i in range(h):
        for j in range(w):
            m.click(i, j)
    print(m._need_explored)
