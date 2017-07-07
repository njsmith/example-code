#!/usr/bin/env python3

# spinner_trio.py

# credits:
# Example from the book Fluent Python by Luciano Ramalho inspired by
# Michele Simionato's multiprocessing example in the python-list:
# https://mail.python.org/pipermail/python-list/2009-February/538048.html

# Modified from the curio example in this directory
# This version has significantly different semantics than the asyncio or curio
# versions, in that if there is an error in spin() or slow_function(),
# then it immediately stops everything and exits with an error; in the
# other versions, errors in spin() are ignored and errors in slow_function()
# leave spin() running in the background with potentially confusing results.
# 
# To see the difference, try adding a typo to one of these functions and then
# see how the three different versions react.

import trio
import itertools
import sys


async def spin(msg):  # <1>
    write, flush = sys.stdout.write, sys.stdout.flush
    try:
        for char in itertools.cycle('|/-\\'):
            status = char + ' ' + msg
            write(status)
            flush()
            write('\x08' * len(status))
            await trio.sleep(.1)  # <2>
    finally:
        write(' ' * len(status) + '\x08' * len(status))

        
async def slow_function():  # <4>
    # pretend waiting a long time for I/O
    await trio.sleep(3)  # <5>
    return 42


# After the main task finishes, we want to cancel the sibling spinner task.
# This does that.
async def main_task_helper(cancel_scope, fn, *args):
    try:
        return await fn(*args)
    finally:
        cancel_scope.cancel()
        

async def supervisor():  # <6>
    async with trio.open_nursery() as nursery:
        nursery.spawn(spin, 'thinking!')  # <7>
        task = nursery.spawn(main_task_helper, nursery.cancel_scope, slow_function)  # <9>
    return task.result.unwrap()


def main():
    result = trio.run(supervisor)  # <11>
    print('Answer:', result)


if __name__ == '__main__':
    main()
