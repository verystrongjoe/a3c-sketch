import time

import tornado
import tornado.websocket

def put(msg):
    print('put(): msg=%s' % msg)

@tornado.gen.coroutine
def process_msgs():
    url = 'ws://localhost:9044?local_agent_id=2'
    client = tornado.httpclient.HTTPRequest(url)
    # conn = yield tornado.websocket.websocket_connect(client, on_message_callback=put)
    conn = yield tornado.websocket.websocket_connect(client)
    conn.read_m
    conn.write_message('send')
    conn.write_message('send')


    print('before sleep')
    time.sleep(10)
    print('after sleep')

tornado.ioloop.IOLoop.instance().run_sync(process_msgs)