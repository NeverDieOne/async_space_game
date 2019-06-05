import time
import curses
import asyncio


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        canvas.addstr(row + 1, column, '1')
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        canvas.addstr(row + 1, column, '2')
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        canvas.addstr(row + 1, column, '3')
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        canvas.addstr(row + 1, column, '4')
        await asyncio.sleep(0)


def draw(canvas, row, column):
    canvas.border()
    curses.curs_set(False)

    coroutine = blink(canvas, row, column)
    while True:
        coroutine.send(None)
        canvas.refresh()
        time.sleep(1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw, 5, 20)
