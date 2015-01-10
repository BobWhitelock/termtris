
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

board_state = [[EMPTY for y in range(COLUMNS)] for x in range(ROWS)]

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


def draw_borders(window):

	# draw top and bottom
	for x in range(COLUMNS + 2):
		window.addstr(0, x, BORDER)
		window.addstr(ROWS+1, x, BORDER)

		# draw sides
	for y in range(ROWS + 2):
		window.addstr(y, 0, BORDER)
		window.addstr(y, COLUMNS+1, BORDER)

	window.refresh()

def draw_board(window):
	for y in range(ROWS):
		for x in range(COLUMNS):
			window.addstr(y+1, x+1, board_state[y][x])
			
	window.refresh()

def drop(shape):
	pass

def __main__(stdscr):
	draw_borders(stdscr)
	draw_board(stdscr)

	block = Tetronimo()
	while (True):
		block.draw(stdscr)
		block.drop()
		time.sleep(0.5)

	stdscr.getkey()


curses.wrapper(__main__)

