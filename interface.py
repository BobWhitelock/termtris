import curses


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