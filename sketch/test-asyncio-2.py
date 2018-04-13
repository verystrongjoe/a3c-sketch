import asyncio
import websockets


async def hello():
    async with websockets.connect('ws://localhost:8765') as websocket:
        name = input("What's your name? ")
        await websocket.send(name)
        print("> {}".format(name))

        greeting = await websocket.recv()
        print("< {}".format(greeting))


asyncio.get_event_loop().run_until_complete(hello())



# import asyncio
#
# async def slow_operation(future):
#     await asyncio.sleep(2)
#     future.set_result('Future is done!')
#
# def got_result(future):
#     print('future.result() ' ,future.result())
#     loop.stop()
#
# loop = asyncio.get_event_loop()
# future = asyncio.Future()
# asyncio.ensure_future(slow_operation(future))
# future.add_done_callback(got_result)
# try:
#     loop.run_forever()
#     print('end!!')
#
# finally:
#     loop.close()