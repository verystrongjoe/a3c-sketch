import asyncio


@asyncio.coroutine
def greet_every_two_seconds():
    while True:
        print('Hello World')
        yield from asyncio.sleep(2)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(greet_every_two_seconds())
    finally:
        loop.close()



# import asyncio
# from asyncio import Queue
#
#
# q = Queue()
#
# async def main():
#
#
#     print(q.empty())  # True
#
#     await q.put(100)
#
#     item  = await q.get()
#
#     # print(q.empty())  # False
#     print(item)
#
#
# if __name__ ==  '__main__':
#     loop = asyncio.get_event_loop()
#     try:
#         loop.run_until_complete(main())
#     finally:
#         loop.run_until_complete(loop.shutdown_asyncgens())
#         loop.close()
#     print(q.empty())  # False







# import asyncio
# import random
#
# async def lazy_greet(msg, delay=1):
#     print(msg, "will be displayed in", delay, "seconds")
#     await asyncio.sleep(delay)
#     return msg.upper()
#
# async def main():
#     messages = ['hello', 'world', 'apple', 'banana', 'cherry']
#     fts = [asyncio.ensure_future(lazy_greet(m, random.randrange(1, 5)))
#            for m in messages]
#     for f in asyncio.as_completed(fts):
#         x = await f
#         print(x)
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()
#



# import asyncio
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
# loop.close()


#
# import asyncio
# import websockets
#
# async def hello(websocket, path):
#     name = await websocket.recv()
#     print("< {}".format(name))
#
#     greeting = "Hello {}!".format(name)
#     await websocket.send(greeting)
#     print("> {}".format(greeting))
#
# start_server = websockets.serve(hello, 'localhost', 8765)
#
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()




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