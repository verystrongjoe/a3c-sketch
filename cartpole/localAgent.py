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


 ## reference!!
 http://websockets.readthedocs.io/en/stable/intro.html#both
 http://websockets.readthedocs.io/en/stable/api.html
 https://soooprmx.com/archives/6882
 https://stackoverflow.com/questions/32054066/python-how-to-run-multiple-coroutines-concurrently-using-asyncio
 https://docs.python.org/3/library/asyncio.html
 http://hamait.tistory.com/834
 http://masnun.com/2015/11/20/python-asyncio-future-task-and-the-event-loop.html
 https://tech.ssut.me/2015/07/09/python-3-play-with-asyncio/
 https://dojang.io/mod/page/view.php?id=1167
'''

# import threading

import cartpole.util as util
import cartpole.network as network

# from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from tornado.websocket import WebSocketClosedError
from tornado.websocket import StreamClosedError

import cartpole.config as config
import tensorflow as tf
from keras import backend as K
import gym
import numpy as np
import json
import logging as logger
import time
import asyncio

from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import httputil
# from tornado import ioloop
# from tornado import websocket

import functools
import json
import time

import websockets

APPLICATION_JSON = 'application/json'
DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60

env = gym.make(config.A3C_ENV['env_name'])

action_size = env.action_space.n
state_size = env.observation_space.shape[0]

actor, critic = network.build_model(state_size, action_size, 24, 24, True)  # declaring here is to share this between WShanlder and global agent


class localAgent():

        async def producer(self):
                if self.weight_queue.count() != 0 :
                        return self.weight_queue.pop()

        async def consumer_hadnler(self, websocket, path):
                async for message in websocket:
                        await self.cb_on_message(message)

        async def producer_handler(self, websocket, path):
                while True:
                        message = await self.producer()
                        await websocket.send(message)

        # async def handler(websocket, path):
        #         consumer_task = asyncio.ensure_future(consumer_handler(websocket))
        #         producer_task = asyncio.ensure_future(producer_handler(websocket))
        #         done, pending = await asyncio.wait(
        #                 [consumer_task, producer_task],
        #                 return_when=asyncio.FIRST_COMPLETED,
        #         )
        #
        #         for task in pending:
        #                 task.cancel()

        # def on_open(self, ws):
        #         print("### Initiating new websocket connection ###")
        #
        # def initiate(self):
        #         websocket.enableTrace(True)
        #         self.ws_2 = websocket.WebSocketApp("ws://localhost:9044?local_agent_id=2",
        #                                     on_message=self.on_message,
        #                                     on_error=self.on_error,
        #                                     on_close=self.on_close)
        #         self.ws_2.on_open = self.on_open
        #
        #         self.ws_2.run_forever()
        #
        # def on_error(error):
        #         print(error)
        #
        # def on_message(message):
        #         print(message)
        #
        # def on_close(self):
        #         print("### closed ###")
        #         # Attemp to reconnect with 2 seconds interval
        #         time.sleep(2)
        #         self.initiate()

        # def send_message(self, action, **data):
        #         """Sends the message to the connected client
        #         """
        #         message = {
        #                 "action": action,
        #                 "data": data
        #         }
        #         try:
        #                 self.write_message(json.dumps(message))
        #         except WebSocketClosedError:
        #                 logger.warning("WS_CLOSED", "Could Not send Message: " + json.dumps(message))
        #                 # Send Websocket Closed Error to Paired Opponent
        #                 self.send_pair_message(action="pair-closed")
        #                 self.close()

        # def __init__(self, global_newtork_ip='localhost', global_newtowrk_port=9044, timeout=5):
        def __init__(self, url, timeout=5):
                # self.actor, self.critic = network.build_model()
                self.ws = None
                self.ws_recv = None
                self.is_connection_closed = False

                self.is_received_msg = False
                self.received_weight = None

                # get size of state and action
                # self.state_size = config.A3C_ENV['state_size']
                # self.action_size = config.A3C_ENV['action_size']
                self.state_size = state_size
                self.action_size = action_size

                # get gym environment name
                self.env_name = config.A3C_ENV['env_name']

                # these are hyper parameters for the A3C
                self.actor_lr = config.A3C_ENV['actor_lr']
                self.critic_lr = config.A3C_ENV['critic_lr']
                self.discount_factor = config.A3C_ENV['discount_factor']
                self.hidden1, self.hidden2 = config.A3C_ENV['hidden1_node'], config.A3C_ENV['hidden2_node']

                self.states, self.actions, self.rewards = [], [], []

                # create model for actor and critic network
                # self.actor, self.critic = network.build_model()

                # method for training actor and critic network
                self.optimizer = [network.actor_optimizer(actor, self.actor_lr, self.action_size),
                                  network.critic_optimizer(critic, self.critic_lr)]

                self.sess = tf.InteractiveSession()
                K.set_session(self.sess)
                self.sess.run(tf.global_variables_initializer())

                self.url = url
                self.episode = 0

                self.weight_queue = []

                self.ioloop = asyncio.get_event_loop()

                # print('1')
                self.connect()
                # print('2')

                # PeriodicCallback(self.keep_alive, 2000).start()

                # print('3')
                # self.ioloop.start()

                # self.client = TestWebSocketClient()
                # self.client.connect(self.url)

                # time.sleep(5)

                try:
                        # ioloop.IOLoop.instance().start()
                        # self.ioloop.start()
                        consumer_task = asyncio.ensure_future(self.consumer_handler(self.ws))
                        producer_task = asyncio.ensure_future(self.producer_handler(self.ws))

                        self.ioloop.run_until_complete()
                        self.ioloop.run_forever()
                except KeyboardInterrupt:
                        self.client.close()

                print('call for run!!!')
                self.run()



        # In Policy Gradient, Q function is not available.
        # Instead agent uses sample returns for evaluating policy
        def discount_rewards(self, rewards, done=True):
                discounted_rewards = np.zeros_like(rewards)
                running_add = 0
                if not done:
                        running_add = critic.predict(np.reshape(self.states[-1], (1, self.state_size)))[0]
                for t in reversed(range(0, len(rewards))):
                        running_add = running_add * self.discount_factor + rewards[t]
                        discounted_rewards[t] = running_add
                return discounted_rewards


        # @gen.coroutine

        async def cb_on_message(self, weight):
                print('we get the gradient from server : {}'.format(weight))
                print('we get the gradient from server : {}'.format(weight))
                print('we get the gradient from server : {}'.format(weight))
                util.set_weight_with_serialized_data(actor, critic, weight)
                return weight

        # @gen.coroutine
        @asyncio.coroutine
        def connect(self):
                print("trying to connect")
                isConnected = False

                while isConnected is False:
                        try:
                                # self.ws = yield websocket_connect(self.url, on_message_callback=self.cb_on_message)
                                self.ws = yield from websocket_connect(self.url)
                                isConnected = True
                        except Exception as e:
                                print("connection error : {}".format(e))
                                isConnected = False

                # self.initiate()
                print("connected")

                # while self.ws is None:
                #         self.ws = yield websocket_connect(self.url, connect_timeout=99999, on_message_callback=cb_on_message)

        # @gen.coroutine
        def get_weight_from_global_network(self):
                # print('get_weight_from_global_network :: trying to get message from global network!!')

                while True:
                        if self.is_connection_closed is True:
                                # print('reconnect!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                                self.connect()
                        else:
                                break
                # print('finished to check the connection and send msg to request weight from server!!')

                # print('get_weight_from_global_network :: send start')

                # self.ws.write_message('send')
                self.client.write_message('send')

                # print('get_weight_from_global_network :: send end')

                # # self.ws2.send('send')
                # while True:
                #     print('trying to get message from global network!!')
                #     msg = yield self.cb_on_message()
                #     print('check')
                #
                #     if msg is None:
                #         print("connection closed")
                #         self.ws = None


        # while future.done() is False :
                #         print('what the!!!!!!!!!!!!!!{}'.future.result())

                # print('what the!!!!!!!!!!!!!!{}'.format(future.done()))

                # while True:
                #         try:
                #                 self.ws.read_message(callback=self.cb_receive_weight)
                #                 # response = yield self.ws.read_message()
                #         except StreamClosedError:
                #                 self._abort()

                        # result = future.result(timeout)  # Wait for the result with a timeout
                        #TODO:  http://masnun.com/2015/11/20/python-asyncio-future-task-and-the-event-loop.html
                        #TODO:  http://www.tornadoweb.org/en/stable/concurrent.html
                        #TODO:  https://www.youtube.com/watch?v=IqoYVfoetFg
                        #TODO:  https://www.youtube.com/watch?v=SkETonolR3U

                        # if response.done():
                        #         print('weight of global network : {} '.format(f.result()))
                                # util.set_weight_with_serialized_data()
                                # break
                #                 print("connection closed")
                #                 # util.set_weight_with_serialized_data(actor, critic, msg)
                #                 self.ws = None
                #         else:
                #                 print('msg is not null!!!!!!!')
                #                 util.set_weight_with_serialized_data(actor, critic, msg)
                #

                # util.get_weight_with_serialized_data(actor, critic)


        # save <s, a ,r> of each step
        # this is used for calculating discounted rewards
        def memory(self, state, action, reward):
                self.states.append(state)
                act = np.zeros(self.action_size)
                act[action] = 1
                self.actions.append(act)
                self.rewards.append(reward)

        @asyncio.coroutine
        def read_message_from_server(self):
            print('trying to get message from server!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('trying to get message from server!!!!!!!!!!!!!!!!!!!!!!!!!!!')

            while True:
                msg = yield self.ws.read_message()
                print(msg)
                future.set_result(msg)
                if msg is None:
                    print("connection closed")
                    self.ws = None
                    break

            # msg = None
            # # while True:
            # msg = await self.ws.read_message()
            #         # if msg is not None:
            #         #         break
            # future.set_result(msg)
            # self.is_received_msg = True
            # self.received_msg = msg
            # print('################ we received {}'.format(msg))

        @gen.coroutine
        def run(self):
                # future = asyncio.Future()
                # asyncio.ensure_future(self.read_message_from_server(future))
                # asyncio.get_event_loop().run_until_complete(future)

                while True:
                    # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    # if asyncio.get_event_loop().is_closed() :
                    #     asyncio.ensure_future(self.read_message_from_server(future))
                    #     asyncio.get_event_loop().run_until_complete(future)
                    self.run_rl()
                    # self.read_message_from_server(future)

                    # if self.is_received_msg:
                    #         util.set_weight_with_serialized_data(actor, critic, self.received_msg)
                    #         self.is_received_msg = False
                    #         self.received_msg = None
                    #         asyncio.get_event_loop().close()


        # @gen.coroutine
        def run_rl(self):
                state = env.reset()
                score = 0
                while True:
                        action = self.get_action(state)
                        next_state, reward, done, _ = env.step(action)
                        score += reward

                        self.memory(state, action, reward)

                        state = next_state

                        if done:
                                self.episode += 1
                                # print("episode: ", self.episode, "/ score : ", score)
                                self.train_episode(score != 500)
                                break
                if self.episode % 3 == 0:
                        self.get_weight_from_global_network()



        # update policy network and value network every episode
        def train_episode(self, done):
                # print('train_episode')
                discounted_rewards = self.discount_rewards(self.rewards, done)

                values = critic.predict(np.array(self.states))
                values = np.reshape(values, len(values))

                advantages = discounted_rewards - values

                self.optimizer[0]([self.states, self.actions, advantages])
                self.optimizer[1]([self.states, discounted_rewards])

                ### send trained neuralnet weights
                weight_data = util.get_weight_with_serialized_data(actor, critic)
                # print('send trained neural-net weights {}'.format(weight_data))

                try:
                        # self.ws.write_message(weight_data, binary=True)
                        # self.client.send(weight_data)
                        self.weight_queue.append(weight_data)

                        # self.ws2.send(weight_data)
                except WebSocketClosedError:
                        logger.warning("WS_CLOSED", "Could Not send Message: " + str(weight_data))
                        # Send Websocket Closed Error to Paired Opponent
                        # self.close()

                self.states, self.actions, self.rewards = [], [], []

        def close(self):
                self.is_connection_closed = True

        def keep_alive(self):

                if self.is_connection_closed :
                        print('keey_alive : disconnected')
                        self.connect()
                else:
                        print('keey_alive : send heart bit message to check ')
                        self.ws.write_message("check")
                        # self.ws2.send("check")

        def get_action(self, state):
                policy = actor.predict(np.reshape(state, [1, self.state_size]))[0]
                return np.random.choice(self.action_size, 1, p=policy)[0]



if __name__ == "__main__":
        localAgent = localAgent("ws://localhost:9044?local_agent_id=2", timeout=50000)

