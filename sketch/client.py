#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
import  random
import sched, time
from threading import Timer

class Client(object):

    def __init__(self, url, timeout):

        # self._url = 'ws://' + ip + ":" + str(port)
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        # PeriodicCallback(self.timer, 1000).start()
        PeriodicCallback(self.send_weight_to_global_network, 1000).start()
        PeriodicCallback(self.get_weight_from_global_network, 3000).start()
        self.ioloop.start()

    def onMsgCallback(self, msg):
        print('we get the gradient from server : {}'.format(msg))

    @gen.coroutine
    def connect(self):
        print("trying to connect")
        try:
            self.ws = yield websocket_connect(self.url, on_message_callback=self.onMsgCallback)
        except Exception as e:
            print("connection error : {}".format(e))
        else:
            print("connected")
            self.run()

    @gen.coroutine
    def run(self):

        while True:
            msg = yield self.ws.read_message()
            print('msg : {}'.format(msg))
            if msg is None:
                print ("connection closed")
                self.ws = None
                break

    def _get_gradient(self):
        return random.random()

    # def timer(self):
        # print('timer...')
        # s = sched.scheduler(time.time, time.sleep)
        # s.enter(1, 1, self.send_weight_to_global_network, ())
        # s.enter(2, 1, self.get_weight_from_global_network, ())
        # s.run()
        # Timer(3, self.get_weight_from_global_network, (self.ioloop)).start()
        # Timer(1, self.send_weight_to_global_network, (self.ioloop)).start()

    def send_weight_to_global_network(self):
        print('send_weight_to_global_network...')
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message(str(self._get_gradient()))

    def get_weight_from_global_network(self):
        print('trying to get message from global network!!')
        if self.ws is None:
            self.connect()
        else:
            # print('!!!')
            self.ws.write_message('send')
            # while True:
                # msg = yield self.ws.read_message()
                # msg = 'a'
                # print('print::::::: {}'.format(msg))

                # if msg is None:
                #     break
            # print ("connection closed")
            # self.ws = None


if __name__ == "__main__":
    client = Client("ws://localhost:9044?local_agent_id=2", 5)
