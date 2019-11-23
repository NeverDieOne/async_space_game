import time
import asyncio
import curses
import random
from curses_tools import draw_frame, read_controls, get_frame_size
import os
from itertools import cycle

TIC_TIMEOUT = 0.1
SYMBOLS = '+*.:'
STARS_AMOUNT = 50


async def blink(canvas, row, column, offset_tics, symbol='*'):
    for _ in range(offset_tics):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column, *frames):
    last_frame = None
    min_x, min_y = 1, 1

    #  canvas.getmaxyx() return tuple of height and width (https://docs.python.org/2/library/curses.html#curses.window.getmaxyx)
    height, width = canvas.getmaxyx()
    max_x, max_y = height - 1, width - 1

    while True:
        for frame in cycle(frames):
            delta_row, delta_column, space = read_controls(canvas)
            frame_rows, frame_columns = get_frame_size(frame)

            if column + delta_column + frame_columns > max_y or column + delta_column + 1 < min_y + 1:
                delta_column = 0
            if row + delta_row + frame_rows > max_x or row + delta_row + 1 < min_x + 1:
                delta_row = 0

            if last_frame:
                draw_frame(canvas, row, column, last_frame, negative=True)

            row = row + delta_row
            column = column + delta_column
            draw_frame(canvas, row, column, frame)

            last_frame = frame

            for _ in range(2):
                await asyncio.sleep(0)


def get_random_xy(max_x, max_y):
    return random.randint(1, max_x - 2), random.randint(1, max_y - 2)


def get_frames_from_files(frames_dir):
    frames = []
    for frame_file in os.listdir(f"{frames_dir}"):
        with open(f"{frames_dir}/{frame_file}") as _file:
            frames.append(_file.read())
    return frames


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    rocket_frames = get_frames_from_files('rocket_frames')

    #  canvas.getmaxyx() return tuple of height and width (https://docs.python.org/2/library/curses.html#curses.window.getmaxyx)
    height, width = canvas.getmaxyx()
    max_x, max_y = height, width

    coroutines = [blink(canvas, *get_random_xy(max_x, max_y), random.randint(0, 10), random.choice(SYMBOLS)) for _ in
                  range(STARS_AMOUNT)]
    coroutines.append(animate_spaceship(canvas, max_x // 2, max_y // 2, *rocket_frames))

    while coroutines:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
