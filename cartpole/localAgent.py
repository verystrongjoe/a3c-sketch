'''
Local Agent

This class can be used to do for things below.
 a. create its own local network using network.py which is same as its global network
 b. set weight of local network with same weight of global network
         - __init__ method
         . get weight from global network when it created
 c. agent interact with environment (train /predict)
 d. generate or calculate its gradient update
 e. send gradient update to global network
 f. __init__  constructor
    . actor
    . critic
    . opitmizer
    . discount_factor
    . action_size
    . state_size
 g. it is inherited from Thread
'''

import threading
import cartpole.util as util
import cartpole.network as network
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect

actor, critic = network.build_model() # declaring here is to share this between WShanlder and global agent

class localAgent():
        # def __init__(self, global_newtork_ip='localhost', global_newtowrk_port=9044, timeout=5):
        def __init__(self, url, timeout=5):
                # self.actor, self.critic = network.build_model()
                # self.ws = None
                self.url = url
                self.ioloop = IOLoop.instance()
                self.connect()
                PeriodicCallback(self.keep_alive, 5000).start()
                self.ioloop.start()

        def cb_receive_weight(self, weight):
                print('we get the gradient from server : {}'.format(weight))
                util.set_weight_with_serialized_data(actor, critic, weight)

        @gen.coroutine
        def connect(self):
                print("trying to connect")
                try:
                        self.ws = yield websocket_connect(self.url)
                        # self.ws = yield websocket_connect(self.url, on_message_callback=self.cb_receive_weight)
                except Exception as e:
                        print("connection error : {0}".format(e))
                else:
                        print("connected")
                        self.run()

        def get_weight_from_global_network(self):
                print('trying to get message from global network!!')

                while True:
                        if self.ws is None:
                                self.connect()
                        else:
                                break
                print('!!!')
                self.ws.write_message('send')

        @gen.coroutine
        def run(self):
                print('run!!')
                #util.get_weight_with_serialized_data(actor, critic)
                while True:
                        msg = yield self.ws.read_message()
                        print('weight : {} '.format(msg))
                        if msg is None:
                                print("connection closed")
                                # util.set_weight_with_serialized_data(actor, critic, msg)
                                self.ws = None
                                break
                        else:
                                print('msg is not null!!!!!!!')
                                util.set_weight_with_serialized_data(actor, critic, msg)

        def keep_alive(self):
                # print('keep alive!!! ws : {}'.format(self.ws))
                if self.ws is None:
                        # print('keey_alive : connect')
                        self.connect()
                else:
                        # print('keey_alive : send msg')
                        self.ws.write_message("send")

if __name__ == "__main__":
        localAgent = localAgent("ws://localhost:9044?local_agent_id=2", timeout=5)


