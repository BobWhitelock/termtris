#!/usr/bin/env python3

import curses
import random
import time
import copy

import pdb

DEBUG = True

BORDER = '#'
FILLED = '■'
EMPTY = ' '

GAP = 4 # gap between spawn zone and sides
ROWS = 25
COLUMNS = 25


def main(stdscr = None):

    if stdscr is None:
        graphics = DebugGraphics()
    else:
        graphics = CursesGraphics(stdscr)

    board = Board(graphics)

    while True:
        board.draw()

        if board.current_block_can_drop():
            board.drop_current_block()
        else:
            board.spawn_block()

        board.update_block_state()
        time.sleep(0.2)


def debug(*args):
    if DEBUG:
        print(*args)


class CursesGraphics:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def set_point(self, x, y, symbol):
        self.stdscr.addstr(y, x, symbol)

    def refresh(self):
        self.stdscr.refresh()


class DebugGraphics:
    def set_point(self, x, y, symbol):
        if symbol != EMPTY:
            debug("({0}, {1}) = '{2}'".format(x, y, symbol))

    def refresh(self):
        debug("REFRESH")


class Board:
    def __init__(self, graphics):
        self.graphics = graphics
        self._draw_borders()
        self.state = [[EMPTY for y in range(COLUMNS)] for x in range(ROWS)]
        self.current_block = None

    def _draw_borders(self):
        # draw top and bottom
        for x in range(COLUMNS + 2): 
            self.graphics.set_point(x, 0, BORDER)
            self.graphics.set_point(x, ROWS+1, BORDER)

        # draw sides
        for y in range(ROWS + 2):
            self.graphics.set_point(0, y, BORDER)
            self.graphics.set_point(COLUMNS+1, y, BORDER)

        self.graphics.refresh()

    def draw(self):
        for y in range(ROWS):
            for x in range(COLUMNS):
                self.graphics.set_point(x+1, y+1, self.state[x][y])
            
        self.graphics.refresh()

    def get_state(self, point):
        if 0 <= point.x < COLUMNS and 0 <= point.y < ROWS:
            return self.state[point.x][point.y]
        else:
            return BORDER

    def set_state(self, point, symbol):
        self.state[point.x][point.y] = symbol

    def spawn_block(self):
        self.current_block = Block()

    def current_block_can_drop(self):
        if self.current_block is None:
            return False
        for position in self.current_block.positions:
            debug("currpos: " + str(position))
            point_below = position.point_below()
            debug("below: " + str(point_below))
            if self.get_state(point_below) != EMPTY:
                return False
        return True

    def drop_current_block(self):
        self.current_block.drop()

    def update_block_state(self):
        for old_position in self.current_block.old_positions:
            self.set_state(old_position, EMPTY)
        for position in self.current_block.positions:
            self.set_state(position, FILLED)

    


class Block:

    SHAPE = ((FILLED, FILLED, FILLED, FILLED))

    def __init__(self):
        self.shape = Block.SHAPE

        top_left_point = Point(random.randrange(GAP, COLUMNS - GAP), 0)

        self.old_positions = set()
        self.positions = set()
        for x, row in enumerate(self.shape):
            for y, point in enumerate(row):
                # debug("here:", x, y)
                if point == FILLED:
                    position = top_left_point + Point(x, y)
                    self.positions.add(position)
                    # debug("here2:", position)

    def drop(self):
        self.old_positions = copy.deepcopy(self.positions)
        for position in self.positions:
            position.lower()
            debug("here:", position)

        # # alt:
        # self.old_positions = deepcopy(self.positions)
        # for point in self.positions:
        #     point = point.point_below()


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({0},{1})'.format(self.x, self.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def lower(self):
        self.y += 1

    def point_below(self):
        return Point(self.x, self.y + 1)


if __name__ == '__main__':
    if DEBUG:
        main()
    else:
        curses.wrapper(main)