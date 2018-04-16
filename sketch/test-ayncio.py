import asyncio
import datetime
import random
import websockets

async def time(websocket, path):
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)

start_server = websockets.serve(time, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

#
# import asyncio
# import random
#
#
# async def lazy_greet(msg, delay=1):
#     print(msg, "will be displayed in", delay, "seconds")
#     await asyncio.sleep(delay)
#     return msg.upper()
#
#
# async def main():
#     messages = ['hello', 'world', 'apple', 'banana', 'cherry']
#     fts = [asyncio.ensure_future(lazy_greet(m, random.randrange(1, 5)))
#            for m in messages]
#     for f in asyncio.as_completed(fts):
#         x = await f
#         print(x)
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.run_forever()
# loop.close()




# import asyncio
# import time
# from tornado import gen
#
# class a :
#
#     async def slow_operation(self, future):
#         print('what the !!!!!!!!!!!!!!!!!!!!!')
#         await asyncio.sleep(2)
#         future.set_result('Future is done!')
#         print('what the !!!!!!!!!!!!!!!!!!!!!2222222222222222')
#
#     @gen.coroutine
#     def run(self):
#         start = time.time()
#         loop = asyncio.get_event_loop()
#         future = asyncio.Future()
#         asyncio.ensure_future(self.slow_operation(future))
#         print('what are you doing??')
#         # loop.run_until_complete(future)
#         time.sleep(3)
#         print(future.result())
#         loop.close()
#         end = time.time()
#
#         print('end-start : {}'.format(end-start))
#
#
# if __name__ == '__main__':
#     cc = a()
#     cc.run()