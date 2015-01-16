#!/usr/bin/env python3

import copy
import curses
import math
import pdb
import random
import time


DEBUG = False

BORDER = '#'
FILLED = '■'
EMPTY = ' '

GAP = 4 # gap between spawn zone and sides
ROWS = 25
COLUMNS = 25

FPS = 60
FRAME_LENGTH = 1 / FPS
FALL_SPEED = 30 if not DEBUG else 0


def main(stdscr = None):

    if stdscr is None:
        graphics = DebugGraphics()
    else:
        graphics = CursesGraphics(stdscr)

    board = Board(graphics)

    frames_until_drop = 0
    while True:
        frame_start_time = time.time()

        board.draw()

        # drop/spawn current block
        if frames_until_drop == 0:
            frames_until_drop = FALL_SPEED
            if board.can_drop_current_block():
                board.drop_current_block()
            else:
                board.spawn_block()
        else:
            frames_until_drop -= 1

        # handle user input
        key = graphics.read_input()
        if key != -1:
            if key in (curses.KEY_LEFT, ord('a')):
                board.move_current_block_left()
            elif key in (curses.KEY_RIGHT, ord('d')):
                board.move_current_block_right()
            elif key in (curses.KEY_UP, ord('w')):
                board.current_block.rotate_clockwise()
            elif key in (curses.KEY_DOWN, ord('s')):
                while board.can_drop_current_block():
                    board.drop_current_block()

        board.update_block_state()

        if not DEBUG:
            frame_length = time.time() - frame_start_time
            frame_sleep = FRAME_LENGTH - frame_length
            time.sleep(frame_sleep)


def debug(*args):
    if DEBUG:
        print(*args)


class CursesGraphics:
    def __init__(self, stdscr):
        curses.curs_set(0) # make cursor invisible
        stdscr.nodelay(1) # make reading input with getch() non-blocking
        self.stdscr = stdscr

    def set_point(self, x, y, symbol):
        self.stdscr.addstr(y, x, symbol)

    def refresh(self):
        self.stdscr.refresh()

    def read_input(self):
        # read first char and skip any others
        key = self.stdscr.getch()
        while self.stdscr.getch() != -1:
            pass
        return key


class DebugGraphics:
    def set_point(self, x, y, symbol):
        if symbol != EMPTY:
            debug("({0}, {1}) = '{2}'".format(x, y, symbol))

    def refresh(self):
        debug("REFRESH")

    def read_input(self):
        user_input = input("Input: ")
        if len(user_input) > 0:
            key = user_input[0]
            debug("Input read: '{0}'; key returned: '{1}'".format(user_input, key))
            return ord(key)
        else:
            return ''


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

    def can_drop_current_block(self):
        if self.current_block is None:
            return False
        for position in self.current_block.below_positions:
            if self.get_state(position.get_point_below()) != EMPTY:
                return False
        return True

    def drop_current_block(self):
        self.current_block.drop()

    def can_move_current_block_left(self):
        if self.current_block is None:
            return False
        for position in self.current_block.left_positions:
            if self.get_state(position.get_point_to_left()) != EMPTY:
                return False
        return True

    def move_current_block_left(self):
        if self.can_move_current_block_left():
            self.current_block.left()

    def can_move_current_block_right(self):
        if self.current_block is None:
            return False
        for position in self.current_block.right_positions:
            if self.get_state(position.get_point_to_right()) != EMPTY:
                return False
        return True

    def move_current_block_right(self):
        if self.can_move_current_block_right():
            self.current_block.right()

    def update_block_state(self):
        for old_position in self.current_block.old_positions:
            self.set_state(old_position, EMPTY)
        self.current_block.old_positions.clear()
        for position in self.current_block.positions:
            self.set_state(position, FILLED)


class Block:

    #TODO better names?

    EMPTY_STATE = 0
    FILLED_STATE = 1
    PIVOT_STATE = 2
    FILLED_STATES = (FILLED_STATE, PIVOT_STATE)

    I_BLOCK = ((FILLED_STATE, FILLED_STATE, PIVOT_STATE, FILLED_STATE), )

    J_BLOCK = ((FILLED_STATE, EMPTY_STATE, EMPTY_STATE),
               (FILLED_STATE, PIVOT_STATE, FILLED_STATE))

    L_BLOCK = ((EMPTY_STATE, EMPTY_STATE, FILLED_STATE),
               (FILLED_STATE, PIVOT_STATE, FILLED_STATE))

    O_BLOCK = ((FILLED_STATE, FILLED_STATE),
               (FILLED_STATE, FILLED_STATE))

    S_BLOCK = ((EMPTY_STATE, PIVOT_STATE, FILLED_STATE),
               (FILLED_STATE, FILLED_STATE, EMPTY_STATE))

    T_BLOCK = ((EMPTY_STATE, PIVOT_STATE, EMPTY_STATE),
               (FILLED_STATE, FILLED_STATE, FILLED_STATE))

    Z_BLOCK = ((FILLED_STATE, PIVOT_STATE, EMPTY_STATE),
               (EMPTY_STATE, FILLED_STATE, FILLED_STATE))

    SHAPES = (I_BLOCK, J_BLOCK, L_BLOCK, O_BLOCK, S_BLOCK, T_BLOCK, Z_BLOCK)

    def __init__(self):
        self.shape = random.choice(Block.SHAPES)
        self._init_positions()
        self.old_positions = set()
        self._generate_position_tracking_sets()

        debug('All positions: ', self.positions)
        debug('Left positions: ', self.left_positions)
        debug('Right positions: ', self.right_positions)
        debug('Below positions: ', self.below_positions)
        debug('Above positions: ', self.above_positions)

    def _init_positions(self):
        #TODO: make top_left_point only give points which will set block within GAP distance from either side - will depend on shape's width
        top_left_point = Point(random.randrange(GAP, COLUMNS - GAP), 0)
        self._set_positions_given_top_left_point(top_left_point)

    def _set_positions_given_top_left_point(self, top_left_point):
        """Create set of positions the block is currently occupying, given
        self.shape and starting from the top_left_point Point parameter.
        """

        self.positions = set()
        self.pivot = None
        for y, column in enumerate(self.shape):
            for x, state in enumerate(column):
                if state in Block.FILLED_STATES:
                    position = top_left_point + Point(x, y)
                    self.positions.add(position)
                    if state is Block.PIVOT_STATE:
                        self.pivot = position

        debug('Pivot: ', self.pivot)

    def _generate_position_tracking_sets(self):
        """Generate sets containing references to the positions currently on
        each of the four sides of the block.
        """

        self.left_positions = set()
        self.right_positions = set()
        self.below_positions = set()
        self.above_positions = set()

        for position in self.positions:
            if position.get_point_to_left() not in self.positions:
                self.left_positions.add(position)
            if position.get_point_to_right() not in self.positions:
                self.right_positions.add(position)
            if position.get_point_below() not in self.positions:
                self.below_positions.add(position)
            if position.get_point_below() not in self.positions:
                self.above_positions.add(position)

    def drop(self):
        self._store_old_positions()
        for position in self.positions:
            position.lower()

    def left(self):
        self._store_old_positions()
        for position in self.positions:
            position.left()

    def right(self):
        self._store_old_positions()
        for position in self.positions:
            position.right()

    def rotate_clockwise(self):
        if self.pivot is not None:
            self._store_old_positions()
            for position in self.positions:
                position.rotate_clockwise_about_point(self.pivot)

    def rotate_anticlockwise(self):
        #TODO
        pass

    def _store_old_positions(self):
        self.old_positions.update(copy.deepcopy(self.positions))


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({0},{1})'.format(self.x, self.y)

    def __repr__(self):
        return 'Point{0}'.format(str(self))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x, self.y == other.x, other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def lower(self):
        self.y += 1

    def left(self):
        self.x -= 1

    def right(self):
        self.x += 1

    def rotate_clockwise_about_point(self, pivot):
        point_relative_to_pivot = self - pivot
        point_relative_to_pivot._rotate_about_origin_by_angle(math.pi / 2)
        rotated_point = point_relative_to_pivot + pivot
        self.x = int(rotated_point.x)
        self.y = int(rotated_point.y)

    def rotate_anticlockwise_about_point(self, pivot):
        pass

    def _rotate_about_origin_by_angle(self, radians):
        x_coeffs = (math.cos(radians), -math.sin(radians))
        y_coeffs = (math.sin(radians), math.cos(radians))

        old_x = copy.deepcopy(self.x)
        old_y = copy.deepcopy(self.y)

        self.x = sum([old_x * coeff for coeff in x_coeffs])
        self.y = sum([old_y * coeff for coeff in y_coeffs])

    def to_left_of(self, other):
        return self.x < other.x

    def to_right_of(self, other):
        return self.x > other.x

    def get_point_below(self):
        return Point(self.x, self.y + 1)

    def get_point_to_left(self):
        return Point(self.x - 1, self.y)

    def get_point_to_right(self):
        return Point(self.x + 1, self.y)


if __name__ == '__main__':
    if DEBUG:
        main()
    else:
        curses.wrapper(main)