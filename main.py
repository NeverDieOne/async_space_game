import time
import curses
import asyncio
import curses
import random
from curses_tools import draw_frame, read_controls
import os
from itertools import cycle

TIC_TIMEOUT = 0.1
SYMBOLS = 'ABCD'
STARS_AMOUNT = 50


async def blink(canvas, row, column, symbol='*'):
    #  Рандомная задержка для каждой звезды чтобы они были ассинхронны.
    for _ in range(random.randint(0, 10)):
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
    while True:
        for frame in cycle(frames):
            if last_frame:
                draw_frame(canvas, row, column, last_frame, negative=True)
            draw_frame(canvas, row, column, frame)
            last_frame = frame
            for _ in range(2):
                await asyncio.sleep(0)
        # row, column, space = read_controls(canvas)
        # await asyncio.sleep(0)
        # draw_frame(canvas, row, column, frames[0], negative=True)
        # draw_frame(canvas, row, column, frames[1])
        # for _ in range(2):
        #     await asyncio.sleep(0)
        # draw_frame(canvas, row, column, frames[1], negative=True)
        # draw_frame(canvas, row, column, frames[0])
        # for _ in range(2):
        #     await asyncio.sleep(0)


def get_random_xy(max_x, max_y):
    return random.randint(1, max_x-2), random.randint(1, max_y-2)


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

    max_x, max_y = canvas.getmaxyx()

    coroutines = [blink(canvas, *get_random_xy(max_x, max_y), random.choice(SYMBOLS)) for _ in range(STARS_AMOUNT)]
    coroutines.append(fire(canvas, max_x-2, 15))
    coroutines.append(animate_spaceship(canvas, max_x//2, max_y//2, *rocket_frames))

    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

