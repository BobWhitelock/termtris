import copy
import math
import random

import config
from debug import debug


#TODO better names? - better location?

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


class Board:
    def __init__(self, graphics):
        self.graphics = graphics
        self._draw_borders()
        self.state = [[config.EMPTY for y in range(config.COLUMNS)] for x in range(config.ROWS)]
        self.current_block = None

    def _draw_borders(self):
        # draw top and bottom
        for x in range(config.COLUMNS + 2):
            self.graphics.set_point(x, 0, config.BORDER)
            self.graphics.set_point(x, config.ROWS+1, config.BORDER)

        # draw sides
        for y in range(config.ROWS + 2):
            self.graphics.set_point(0, y, config.BORDER)
            self.graphics.set_point(config.COLUMNS+1, y, config.BORDER)

        self.graphics.refresh()

    def draw(self):
        for y in range(config.ROWS):
            for x in range(config.COLUMNS):
                self.graphics.set_point(x+1, y+1, self.state[x][y])

        self.graphics.refresh()

    def get_state(self, point):
        if 0 <= point.x < config.COLUMNS and 0 <= point.y < config.ROWS:
            return self.state[point.x][point.y]
        else:
            return config.BORDER

    def set_state(self, point, symbol):
        self.state[point.x][point.y] = symbol

    def spawn_block(self):
        self.current_block = Block()

    def can_drop_current_block(self):
        if self.current_block is None:
            return False
        for position in self.current_block.below_positions:
            if self.get_state(position.get_point_below()) != config.EMPTY:
                return False
        return True

    def drop_current_block(self):
        self.current_block.drop()

    def can_move_current_block_left(self):
        if self.current_block is None:
            return False
        for position in self.current_block.left_positions:
            if self.get_state(position.get_point_to_left()) != config.EMPTY:
                return False
        return True

    def move_current_block_left(self):
        if self.can_move_current_block_left():
            self.current_block.left()

    def can_move_current_block_right(self):
        if self.current_block is None:
            return False
        for position in self.current_block.right_positions:
            if self.get_state(position.get_point_to_right()) != config.EMPTY:
                return False
        return True

    def move_current_block_right(self):
        if self.can_move_current_block_right():
            self.current_block.right()

    def rotate_current_block_clockwise(self):
        self.current_block.rotate_clockwise()

    def rotate_current_block_anticlockwise(self):
        self.current_block.rotate_anticlockwise()

    def update_block_state(self):
        for old_position in self.current_block.old_positions:
            self.set_state(old_position, config.EMPTY)
        self.current_block.old_positions.clear()
        for position in self.current_block.positions:
            self.set_state(position, config.FILLED)
            debug('Position:', position)


class Block:
    def __init__(self):
        self.shape = random.choice(SHAPES)
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
        top_left_point = Point(random.randrange(config.GAP, config.COLUMNS - config.GAP), 0)
        self._set_positions_given_top_left_point(top_left_point)

    def _set_positions_given_top_left_point(self, top_left_point):
        """Create set of positions the block is currently occupying, given
        self.shape and starting from the top_left_point Point parameter.
        """

        self.positions = set()
        self.pivot = None
        for y, column in enumerate(self.shape):
            for x, state in enumerate(column):
                if state in FILLED_STATES:
                    position = top_left_point + Point(x, y)
                    self.positions.add(position)
                    if state is PIVOT_STATE:
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

    def __repr__(self):
        return '[Point({0},{1}) - id:{2}]'.format(self.x, self.y, id(self))

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
        debug('\n', 'Original point:', self)
        point_relative_to_pivot = self - pivot
        debug('Point relative to pivot:', point_relative_to_pivot)
        point_relative_to_pivot._rotate_about_origin_by_angle(math.pi / 2)
        debug('Point relative to pivot rotated:', point_relative_to_pivot)
        rotated_point = point_relative_to_pivot + pivot
        self.x = int(rotated_point.x)
        self.y = int(rotated_point.y)
        debug('Rotated original point:', self, '\n')

    def rotate_anticlockwise_about_point(self, pivot):
        pass

    def _rotate_about_origin_by_angle(self, radians):
        rotation_matrix = ((math.cos(radians), -math.sin(radians)),
                           (math.sin(radians), math.cos(radians)))

        old_x = copy.deepcopy(self.x)
        old_y = copy.deepcopy(self.y)

        self.x = int(round(rotation_matrix[0][0]*old_x + rotation_matrix[0][1]*old_y))
        self.y = int(round(rotation_matrix[1][0]*old_x + rotation_matrix[1][1]*old_y))

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