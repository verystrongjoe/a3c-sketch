import  random
import threading
import time
from tornado.websocket import websocket_connect

class localAgent(threading.Thread):

    port = 0
    threadID = 0
    ip = 'localhost'
    _url = ip + ":" + port
    _websocket_connection = None

    def __init__(self, threadID, ip, port):
        print('Thread ID : {}, IP: {}. Port: {}'.format(threadID, ip, port))
        self.threadID = threadID
        self.port = port
        self.ip = ip
        self._url = 'http://' + ip + ":" + port
        self._websocket_connection = yield websocket_connect(self._url)

    def _get_gradient(thr):
        for i in range(1000):
            yield random.random()

    def _send_to_main_network(self):
        sending_value = self._get_gradient()
        print('{} is sending to {}'.format(sending_value. self._url))
        self._websocket_connection.write_message(sending_value)
        return sending_value

    def run(self):
        while True:
            v = self._send_to_main_network()
            if v is None :
                break
            time.sleep(1)