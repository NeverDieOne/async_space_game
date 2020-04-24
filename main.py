import time
import asyncio
import curses
import random
from curses_tools import draw_frame, read_controls, get_frame_size
from itertools import cycle
from utils import get_frames_from_files, get_random_xy
from physics import update_speed
from obstacles import show_obstacles, Obstacle

TIC_TIMEOUT = 0.1
SYMBOLS = '+*.:'
STARS_AMOUNT = 50
COROUTINES = []
OBSTACLES = []
SPACESHIP_FRAME = ''
OBSTACLES_IN_LAST_COLLISION = []


async def blink(canvas, row, column, offset_tics, symbol='*'):
    await sleep(offset_tics)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


async def fire(canvas, start_row, start_column, rows_speed=-0.5, columns_speed=0):
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

        for obstacle in OBSTACLES:
            obj_corner = row, column
            if obstacle.has_collision(*obj_corner):
                OBSTACLES_IN_LAST_COLLISION.append(obstacle)
                return None


async def animate_spaceship(rocket_frames):
    global SPACESHIP_FRAME

    for frame in cycle(rocket_frames):
        SPACESHIP_FRAME = frame
        await sleep(2)


async def run_spaceship(canvas, row, column):
    global SPACESHIP_FRAME
    last_frame = SPACESHIP_FRAME

    min_x, min_y = 1, 1

    #  canvas.getmaxyx() return tuple of height and width (https://docs.python.org/2/library/curses.html#curses.window.getmaxyx)
    height, width = canvas.getmaxyx()
    max_x, max_y = height - 1, width - 1
    row_speed = column_speed = 0

    while True:
        delta_row, delta_column, space = read_controls(canvas)
        frame_rows, frame_columns = get_frame_size(SPACESHIP_FRAME)

        if space:
            COROUTINES.append(fire(canvas, row - 1, column + 2))

        row_speed, column_speed = update_speed(row_speed, column_speed, delta_row, delta_column)

        if column + delta_column + frame_columns > max_y or column + delta_column + 1 < min_y + 1:
            column_speed = 0
        if row + delta_row + frame_rows > max_x or row + delta_row + 1 < min_x + 1:
            row_speed = 0
        if last_frame:
            draw_frame(canvas, row, column, last_frame, negative=True)

        row += row_speed
        column += column_speed
        draw_frame(canvas, row, column, SPACESHIP_FRAME)

        last_frame = SPACESHIP_FRAME
        await sleep(1)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    global OBSTACLES
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    obstacle_row_size, obstacle_column_size = get_frame_size(garbage_frame)
    garbage_obstacle_frame = Obstacle(row, column, obstacle_row_size, obstacle_column_size)
    OBSTACLES.append(garbage_obstacle_frame)

    await sleep(1)
    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        garbage_obstacle_frame.row += speed

        for obstacle in OBSTACLES_IN_LAST_COLLISION:
            if garbage_obstacle_frame is obstacle:
                OBSTACLES.remove(garbage_obstacle_frame)
                return


async def fill_orbit_with_garbage(canvas, garbage_frames, offset_appear):
    max_columns = canvas.getmaxyx()[1]

    while True:
        await sleep(offset_appear)
        COROUTINES.append(fly_garbage(canvas, random.randint(1, max_columns), random.choice(garbage_frames)))


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    rocket_frames = get_frames_from_files('rocket_frames')
    garbage_frames = get_frames_from_files('garbage')

    #  canvas.getmaxyx() return tuple of height and width (https://docs.python.org/2/library/curses.html#curses.window.getmaxyx)
    height, width = canvas.getmaxyx()
    max_x, max_y = height, width

    COROUTINES.extend([
        blink(canvas, *get_random_xy(max_x, max_y), random.randint(0, 10), random.choice(SYMBOLS)) for _ in
        range(STARS_AMOUNT)
    ])
    COROUTINES.append(animate_spaceship(rocket_frames))
    COROUTINES.append(run_spaceship(canvas, max_x // 2, max_y // 2))
    COROUTINES.append(fill_orbit_with_garbage(canvas, garbage_frames, random.randint(20, 30)))
    COROUTINES.append(show_obstacles(canvas, OBSTACLES))

    while COROUTINES:
        for coroutine in COROUTINES:
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
