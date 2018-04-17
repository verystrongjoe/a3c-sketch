import tornado.websocket
import tornado.ioloop

ioloop = tornado.ioloop.IOLoop.current()

def clbk(message):
    print('received', message)

async def main():
    url = 'ws://localhost:8344'
    conn = await tornado.websocket.websocket_connect(
        url, io_loop=ioloop, on_message_callback=clbk)
    print('get connection')
    while True:
        # print(await conn.read_message())  # The execution hangs here
        st = input()
        print('get msg from input : {}'.format(st))
        await conn.write_message(st)
        print('succeed to send msg')

ioloop.run_sync(main)