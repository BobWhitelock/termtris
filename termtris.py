#!/usr/bin/env python3

import curses
import random
import time

import pdb

BORDER = '#'
FILLED = '■'
EMPTY = ' '

GAP = 4 # gap between spawn zone and sides
ROWS = 25
COLUMNS = 25


def main(stdscr):
    board = Board(stdscr)

    while True:
        board.draw()

        # stdscr.getkey() # pause execution until key press

        # stdscr.addstr(str(board.current_block_can_drop()))
        # if board.current_block is not None:
        #     for position in board.current_block.positions:
        #         stdscr.addstr(str(position))

        pdb.set_trace()

        if board.current_block_can_drop():
            board.drop_current_block()
            # print("here")
            # stdscr.getkey() # pause execution until key press
        else:
            # print("here")
            board.spawn_block()

        board.update_block_state()
        time.sleep(0.5)

    stdscr.getkey() # pause execution until key press


class Board:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self._draw_borders()
        self.state = [[EMPTY for y in range(COLUMNS)] for x in range(ROWS)]
        self.current_block = None

    def _draw_borders(self):
        # draw top and bottom
        for x in range(COLUMNS + 2): 
            self.stdscr.addstr(0, x, BORDER)
            self.stdscr.addstr(ROWS+1, x, BORDER)

        # draw sides
        for y in range(ROWS + 2):
            self.stdscr.addstr(y, 0, BORDER)
            self.stdscr.addstr(y, COLUMNS+1, BORDER)

        self.stdscr.refresh()

    def draw(self):
        for y in range(ROWS):
            for x in range(COLUMNS):
                self.stdscr.addstr(y+1, x+1, self.state[y][x])
            
        self.stdscr.refresh()

    def get_state(self, point):
        if 0 <= point.x < COLUMNS and 0 <= point.y < ROWS:
            return self.state[point.x][point.y]
        else:
            return BORDER

    def spawn_block(self):
        self.current_block = Block()

    def current_block_can_drop(self):
        if self.current_block is None:
            return False
        for position in self.current_block.positions:
            point_below = position.point_below()
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

    def set_state(self, point, symbol):
        self.state[point.x][point.y] = symbol


class Block:

    SHAPE = ((FILLED, FILLED, FILLED, FILLED))

    def __init__(self):
        self.shape = Block.SHAPE
        top_left_pos = Point(random.randrange(0, COLUMNS - GAP), 0)
        self.old_positions = set()
        self.positions = set()
        for y, row in enumerate(self.shape):
            for x, point in enumerate(self.shape[y]):
                if point == FILLED:
                    self.positions.add(Point(x, y))

    def drop(self):
        self.old_positions = positions.copy()
        for point in self.positions:
            new_point = point.point_below()
            self.positions.remove(point)
            self.positions.add(new_point)

        # alt:
        # self.old_positions = positions.deepcopy()
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

    def point_below(self):
        return Point(self.x, self.y + 1)


if __name__ == '__main__':
    curses.wrapper(main)