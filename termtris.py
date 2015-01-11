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


SHAPE = ((EMPTY, EMPTY, EMPTY, EMPTY),
		 (FILLED, FILLED, FILLED, FILLED))

class Tetronimo:

	def __init__(self):
		self.top_x = random.randrange(1 + GAP, ROWS - GAP)
		self.top_y = 0
		self.shape = SHAPE
		self.current_coords = set()

	def drop(self):
		self.top_y += 1

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

	def _clear(self, window):
		for (x, y) in self.current_coords:
			window.addstr(y, x, EMPTY)


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

def main(stdscr):
	board = Board(stdscr)
	board.draw()

	block = Tetronimo()
	while (True):
		block.draw(stdscr)
		block.drop()
		time.sleep(0.5)

	stdscr.getkey()


curses.wrapper(main)

