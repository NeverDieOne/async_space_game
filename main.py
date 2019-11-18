import time
import curses
import asyncio
import curses
import random

TIC_TIMEOUT = 0.1
SYMBOLS = '+*.:'
STARS_AMOUNT = 50


def get_random_xy(max_x, max_y):
    return random.randint(1, max_x-2), random.randint(1, max_y-2)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()

    max_x, max_y = canvas.getmaxyx()
    coroutines = [blink(canvas, *get_random_xy(max_x, max_y), random.choice(SYMBOLS)) for _ in range(STARS_AMOUNT)]
    coroutines.append(fire(canvas, max_x-2, 15))

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


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

