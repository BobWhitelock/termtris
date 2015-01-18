#!/usr/bin/env python3

import curses
import pdb
import time

import config
import interface
import game


def main(stdscr = None):

    if stdscr is None:
        graphics = interface.DebugGraphics()
    else:
        graphics = interface.CursesGraphics(stdscr)

    board = game.Board(graphics)

    frames_until_drop = 0
    while True:
        frame_start_time = time.time()

        board.draw()

        # drop/spawn current block
        if frames_until_drop == 0:
            frames_until_drop = config.FALL_SPEED
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
                board.rotate_current_block_clockwise()
            elif key in (curses.KEY_DOWN, ord('s')):
                while board.can_drop_current_block():
                    board.drop_current_block()

        board.update_block_state()

        if not config.DEBUG:
            frame_length = time.time() - frame_start_time
            frame_sleep = config.FRAME_LENGTH - frame_length
            time.sleep(frame_sleep)


if __name__ == '__main__':
    if config.DEBUG:
        main()
    else:
        curses.wrapper(main)