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


class BoomException(BaseException):
    pass


class WinException(BaseException):
    pass


class Map(object):

    EMPTY = ' '
    UNEXPLORED = '_'
    SAFE = '&'
    FLAG = '#'
    MINE = '*'
    EXPLODE_MINE = 'X'

    def __init__(self, height, width, mine_count, stdout=True):
        logger.info('a new map generated')
        if mine_count > height * width - 9:
            raise Exception('no enough space to place mine')
        self._height = height
        self._width = width
        self._mine_count = mine_count
        self._size = height * width
        self._initialized = False
        self._stdout = stdout

        self._cell_remain = height * width
        self._mine_remain = mine_count
        self._click = 0

        self._map = []
        self._map_visible = []
        for i in range(self._height):
            self._map.append([0] * self._width)
            self._map_visible.append([self.UNEXPLORED] * self._width)
        self._print_map()

    def _print_map(self):
        if not self._stdout:
            return
        os.system('clear')
        print('mines: %4s/%s\tunexplored:%4s/%s\tclick:%4s\n' % (
            self._mine_remain, self._mine_count,
            self._cell_remain, self._size,
            self._click,
        ))
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
        self._click += 1
        if not self._initialized:
            self._initialized = True
            self._initMap(x, y)
            self._extend(x, y)
        elif self._map[x][y] == self.MINE:
            self._boom(x, y)
        elif self._map_visible[x][y] == self.UNEXPLORED:
            self._extend(x, y)
        if self._cell_remain == 0:
            raise WinException()

    @_refresh_map
    def right_click(self, x, y):
        self._click += 1
        if self._map_visible[x][y] == self.FLAG:
            self._cell_remain += 1
            if self._map[x][y] == self.MINE:
                self._mine_remain += 1
            self._setVisible(x, y, self.UNEXPLORED)
        elif self._map_visible[x][y] == self.UNEXPLORED:
            self._cell_remain -= 1
            if self._map[x][y] == self.MINE:
                self._mine_remain -= 1
            self._setVisible(x, y, self.FLAG)
        if self._cell_remain == 0 and self._mine_remain == 0:
            raise WinException()

    @_refresh_map
    def double_click(self, x, y):
        self._click += 1
        for i, j in self._around(x, y):
            if self._map_visible[i][j] == self.UNEXPLORED:
                self.click(i, j)

    def get_visible_map(self):
        return self._map_visible

    def get_statistics(self):
        return {
            'mine_remain': self._mine_remain,
            'cell_remain': self._cell_remain,
        }

    def _boom(self, x, y):
        for i in range(self._height):
            for j in range(self._width):
                if self._map[i][j] == self.MINE:
                    self._setVisible(i, j, self.MINE)
        self._setVisible(x, y, self.EXPLODE_MINE)
        raise BoomException()

    def _win(self):
        for i in range(self._height):
            for j in range(self._width):
                if self._map[i][j] == self.MINE:
                    self._setVisible(i, j, self.FLAG)
        raise WinException()

    def _setMine(self, x, y):
        '''
        setup a mine at (i, j) cell
        '''
        self._map[x][y] = self.MINE
        for i, j in self._around(x, y):
            if self._map[i][j] == self.MINE:
                continue
            self._map[i][j] += 1

    def _setVisible(self, x, y, c):
        self._map_visible[x][y] = c

    def _initMap(self, x, y):
        '''
        initialize map, cell(x, y) should not coutain a mine.
        '''
        n = self._mine_count
        xs = set([x - 1, x, x + 1])
        ys = set([y - 1, y, y + 1])
        while n > 0:
            i = int(random.random() * self._height)
            j = int(random.random() * self._width)
            if self._map[i][j] == self.MINE:
                continue
            if i in xs and j in ys:
                continue
            self._setMine(i, j)
            n -= 1
        for i in range(self._height):
            for j in range(self._width):
                if self._map[i][j] == 0:
                    self._map[i][j] = self.EMPTY

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
            if self._map_visible[i][j] == self.UNEXPLORED:
                self._cell_remain -= 1
            self._setVisible(i, j, self._map[i][j])
            if self._map[i][j] != self.EMPTY:
                continue
            for p, q in self._around(i, j):
                if self._map_visible[p][q] == self.UNEXPLORED:
                    s.append((p, q))


if __name__ == '__main__':
    h = 10
    w = 10
    m = Map(h, w, 10)
    m.click(5, 5)
    import IPython
    IPython.embed()
