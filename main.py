import time
import asyncio
import curses
import random
from curses_tools import draw_frame, read_controls, get_frame_size
from itertools import cycle
from utils import get_frames_from_files, get_random_xy
from physics import update_speed
from obstacles import show_obstacles, Obstacle
from explosion import explode

TIC_TIMEOUT = 0.1
SYMBOLS = '+*.:'
STARS_AMOUNT = 50
COROUTINES = []
OBSTACLES = []
SPACESHIP_FRAME = ''
OBSTACLES_IN_LAST_COLLISION = []
DEBUG = False
YEAR = 1957
PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}


async def change_year():
    global YEAR

    while True:
        await sleep(15)
        YEAR += 1


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


async def show_phrase(canvas):
    while True:
        try:
            draw_frame(canvas, 0, 0, f'Year - {YEAR}: {PHRASES[YEAR]}')
        except KeyError:
            try:
                draw_frame(canvas, 0, 0, f'Year - {YEAR - 1}: {PHRASES[YEAR - 1]}', negative=True)
            except KeyError:
                pass
            draw_frame(canvas, 0, 0, f'Year - {YEAR}')
        await sleep(1)


async def fire(canvas, start_row, start_column, rows_speed=-1, columns_speed=0):
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


async def print_game_over(canvas, raw, column, text):
    while True:
        draw_frame(canvas, raw, column, text)
        await sleep(1)


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

        if space and YEAR >= 2020:
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

        for obstacle in OBSTACLES:
            obj_corner = row, column
            if obstacle.has_collision(*obj_corner):
                with open('game_over_frame.txt', 'r') as game_over_file:
                    game_over_text = game_over_file.read()
                game_over_x, game_over_y = get_frame_size(game_over_text)
                COROUTINES.append(print_game_over(canvas, max_x / 2 - game_over_x, max_y / 2 - game_over_y / 2, game_over_text))
                draw_frame(canvas, row, column, last_frame, negative=True)
                draw_frame(canvas, row, column, SPACESHIP_FRAME, negative=True)
                return

        last_frame = SPACESHIP_FRAME
        await sleep(1)


async def fly_garbage(canvas, column, garbage_frame, speed=1):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    global OBSTACLES
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
                await explode(canvas, row, column)
                return


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


async def fill_orbit_with_garbage(canvas, garbage_frames):
    max_width = canvas.getmaxyx()[1]

    while True:
        offset_appear = get_garbage_delay_tics(YEAR)
        if not offset_appear:
            await sleep(1)
            continue
        await sleep(offset_appear)
        COROUTINES.append(fly_garbage(canvas, random.randint(1, max_width), random.choice(garbage_frames)))


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)

    rocket_frames = get_frames_from_files('rocket_frames')
    garbage_frames = get_frames_from_files('garbage')

    #  canvas.getmaxyx() return tuple of height and width (https://docs.python.org/2/library/curses.html#curses.window.getmaxyx)
    height, width = canvas.getmaxyx()
    max_x, max_y = height - 1, width - 1

    canvas_for_phrase = canvas.derwin(max_x - 2, max_y // 2)

    COROUTINES.extend(
        [blink(canvas, *get_random_xy(max_x, max_y), random.randint(0, 10), random.choice(SYMBOLS)) for _ in
         range(STARS_AMOUNT)]
    )
    COROUTINES.extend([
        animate_spaceship(rocket_frames),
        run_spaceship(canvas, max_x // 2, max_y // 2),
        fill_orbit_with_garbage(canvas, garbage_frames),
        show_phrase(canvas_for_phrase),
        change_year()
    ])
    if DEBUG:
        COROUTINES.append(show_obstacles(canvas, OBSTACLES))  # добавление рамок для мусора

    while COROUTINES:
        for coroutine in COROUTINES.copy():
            canvas.border()
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
