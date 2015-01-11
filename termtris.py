#!/usr/bin/env python3

import curses
import random
import time

# stdscr = curses.initscr()
# stdscr.refresh()

BORDER = '#'
FILLED = '■'
EMPTY = ' '


GAP = 4 # gap between spawn zone and sides
ROWS = 25
COLUMNS = 25


SHAPE = ((FILLED, FILLED, FILLED, FILLED))


# class Point:

# 	def __init__(self, x, y):
# 		self.x = x
# 		self.y = y

# 	def point_below(self):
# 		return Point(self.x, self.y - 1)


class Tetronimo:

	def __init__(self):
		self.top_x = random.randrange(1 + GAP, ROWS - GAP)
		self.top_y = 0
		self.shape = SHAPE
		self.current_coords = set()
		self.old_coords = set()
		self._update_current_coords()

	def drop(self):
		self.top_y += 1
		self._update_current_coords()

	def _update_current_coords(self):
		# add current coords to old coords to be cleared
		for coord in self.current_coords:
			self.old_coords.add(coord)

		# set new current coords
		self.current_coords.clear()
		for y, row in enumerate(self.shape):
			for x, pixel in enumerate(self.shape[y]):
				if (pixel != EMPTY):
					coord_x = self.top_x + x
					coord_y = self.top_y + y
					self.current_coords.add((coord_x, coord_y))

	def _clear(self, window):
		for (x, y) in self.current_coords:
			window.addstr(y, x, EMPTY)

	def draw(self, window):
		self._clear(window)
		for y, row in enumerate(self.shape):
			for x, pixel in enumerate(self.shape[y]):
				if (pixel != EMPTY):
					new_x = self.top_x + x
					new_y = self.top_y + y
					window.addstr(new_y, new_x, pixel)
					self.current_coords.add((new_x, new_y))
		window.refresh()


class Board:
	def __init__(self, stdscr):
		self.stdscr = stdscr
		self._draw_borders()
		self.state = [[EMPTY for y in range(COLUMNS)] for x in range(ROWS)]

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

	def set_block(self, block):
		for coord in block.old_coords:
			self._empty_point(coord)

		block.old_coords.clear()

		for coord in block.current_coords:
			self._fill_point(coord)

	def _empty_point(self, point):
		self._set_point(EMPTY)

	def _fill_point(self):
		self._set_point(FILLED)

	def _set_point(self, point, char):
		self.state[point[0], point[1]] = char

	def point_state(self, x, y):
		if 0 <= x < COLUMNS and 0 <= y < ROWS:
			return self.state[x][y]
		else:
			return BORDER

	def can_drop(self, block):
		for point in block.current_coords:
			point_below = (point[0], point[1] + 1)
			if self.point_state(point_below[0], point_below[1]) != EMPTY:
				return False
		return True


def main(stdscr):
	board = Board(stdscr)
	board.draw()

	block = Tetronimo()
	while (True):
		board.draw()
		# block.draw(stdscr)
		if (board.can_drop(block)):
			block.drop()
		time.sleep(0.5)

	stdscr.getkey()


curses.wrapper(main)

