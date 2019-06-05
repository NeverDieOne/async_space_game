import time
import curses
import asyncio
import random

TIC_TIMEOUT = 0.1
SYMBOLS = '+*.:'
STARS_AMOUNT = 200


async def blink(canvas, symbol):
    max_x, max_y = canvas.getmaxyx()
    x, y = random.randint(1, max_x - 2), random.randint(1, max_y - 2)

    while True:
        canvas.addstr(x, y, symbol, curses.A_DIM)
        canvas.addstr(1, 1, '1')
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(x, y, symbol)
        canvas.addstr(1, 1, '2')
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(x, y, symbol, curses.A_BOLD)
        canvas.addstr(1, 1, '3')
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(x, y, symbol)
        canvas.addstr(1, 1, '4')
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)

    coroutines = [blink(canvas, random.choice(SYMBOLS)) for _ in range(STARS_AMOUNT)]

    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
