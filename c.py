import time

import tornado
import tornado.websocket
from threading import Timer

@tornado.gen.coroutine
def process_msgs():
    url = 'ws://localhost:9044?local_agent_id=2'
    client = tornado.httpclient.HTTPRequest(url)
    conn = yield tornado.websocket.websocket_connect(client, on_message_callback=put)
    # conn = yield tornado.websocket.websocket_connect(client)
    conn.write_message('send')

    print('before sleep')
    time.sleep(2)
    print('after sleep')

tornado.ioloop.IOLoop.instance().run_sync(process_msgs)


def get_weight_from_global_network(msg):
    print('put(): msg=%s' % msg)

def send_weight_to_global_network(msg):
    print('put(): msg=%s' % msg)


Timer(3, get_weight_from_global_network, ('a')).start()
Timer(1, send_weight_to_global_network, ('b')).start()

