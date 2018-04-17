import asyncio
import datetime


async def display_date2(loop):
    end_time = loop.time() + 5.0
    while True:
        print(datetime.datetime.now())
        print('1')
        if (loop.time() + 1.0) >= end_time:
            break
        await asyncio.sleep(2)


async def display_date(loop):
    end_time = loop.time() + 5.0
    while True:
        print(datetime.datetime.now())
        print('2')
        if (loop.time() + 1.0) >= end_time:
            break
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
# Blocking call which returns when the display_date() coroutine is done
loop.run_until_complete(asyncio.gather(display_date(loop), display_date2(loop)))
loop.close()