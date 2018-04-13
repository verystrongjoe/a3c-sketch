


import asyncio
import websockets

async def hello(websocket, path):
    name = await websocket.recv()
    print("< {}".format(name))

    greeting = "Hello {}!".format(name)
    await websocket.send(greeting)
    print("> {}".format(greeting))

start_server = websockets.serve(hello, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()




# import asyncio
#
#
# async def factorial(name, number):
#     f = 1
#     for i in range(2, number+1):
#         print("Task %s: Compute factorial(%s)..." % (name, i))
#         await asyncio.sleep(1)
#         f *= i
#     print("Task %s: factorial(%s) = %s" % (name, number, f))
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.gather(
#     factorial("A", 2),
#     factorial("B", 3),
#     factorial("C", 4),
# ))
# print('end!!')
# loop.close()