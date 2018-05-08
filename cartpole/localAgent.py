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
import binascii

import cartpole.util as util
import cartpole.network as network

from tornado import gen
from tornado.websocket import websocket_connect
from tornado.websocket import WebSocketClosedError
from tornado.websocket import StreamClosedError
from tornado.ioloop import IOLoop, PeriodicCallback

import cartpole.config as config
import tensorflow as tf
from keras import backend as K
import gym
import numpy as np
import json
import logging as logger
import time
import asyncio
from asyncio import Queue

import functools
import json
import time
import pickle
import logging
import traceback

APPLICATION_JSON = 'application/json'
DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60

env = gym.make(config.A3C_ENV['env_name'])
action_size = env.action_space.n
state_size = env.observation_space.shape[0]

# declaring here is to share this between WShanlder and global agent
actor, critic = network.build_model(state_size, action_size, 24, 24, True)

class localAgent():

        def __init__(self, url,  global_newtork_ip='localhost', global_newtowrk_port=9044, timeout=5):

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
                # self.optimizer = [network.actor_optimizer(actor, self.actor_lr, self.action_size),
                #                   network.critic_optimizer(critic, self.critic_lr)]

                self.get_gradient_functions = [
                        network.get_gradients_from_actor(actor), network.get_gradients_from_critic(critic)
                ]

                self.sess = tf.InteractiveSession()
                K.set_session(self.sess)
                self.sess.run(tf.global_variables_initializer())

                self.url = url
                self.episode = 0

                self.ioloop = IOLoop.instance()
                self.connect()

                # PeriodicCallback(self.keep_alive, 2000).start()
                self.ioloop.start()

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

        @gen.coroutine
        def cb_on_message(self, weight):
                # logger.debug('we get the gradient from server : {}'.format(weight))
                logging.debug('we get the gradient from server : {}'.format(weight))
                if weight is not None :
                        util.set_weight_with_serialized_data(actor, critic, weight)

        @gen.coroutine
        def connect(self):
                logging.debug("trying to connect")
                isConnected = False

                while isConnected is False:
                        try:
                                self.ws = yield websocket_connect(self.url, on_message_callback=self.cb_on_message)
                                # self.ws = yield from websockets.connect(self.url)
                                isConnected = True
                        except Exception as e:

                                logging.debug("connection error : {}".format(e))
                                isConnected = False

                # self.initiate()
                logging.debug("connected")
                self.run()

        @gen.coroutine
        def get_weight_from_global_network(self):
                logger.debug('get_weight_from_global_network :: trying to get message from global network!!')
                while True:
                        if self.is_connection_closed is True:
                                # print('reconnect..')
                                self.connect()
                        else:
                                break

                yield self.ws.write_message('send')
                yield gen.sleep(0.1)

        # save <s, a ,r> of each step. this is used for calculating discounted rewards
        def memory(self, state, action, reward):
                self.states.append(state)
                act = np.zeros(self.action_size)
                act[action] = 1
                self.actions.append(act)
                self.rewards.append(reward)

        @gen.coroutine
        def run(self):
                while True:
                        state = env.reset()
                        score = 0

                        if self.episode % 3 == 0:
                                yield self.get_weight_from_global_network()

                        while True:
                                action = self.get_action(state)
                                next_state, reward, done, _ = env.step(action)
                                score += reward

                                self.memory(state, action, reward)

                                state = next_state

                                if done:
                                        self.episode += 1
                                        # self.train_episode(score != 500)
                                        self.send_gradient_to_global_agent(score != 500)
                                        logging.debug("episode: ", self.episode, "/ score : ", score)
                                        break

        # update policy network and value network every episode
        @gen.coroutine
        def send_gradient_to_global_agent(self, done):
        # def train_episode(self, done):
                # print('train_episode')
                discounted_rewards = self.discount_rewards(self.rewards, done)

                values = critic.predict(np.array(self.states))
                values = np.reshape(values, len(values))

                advantages = discounted_rewards - values

                grads_actor = self.get_gradient_functions[0]([self.states, self.actions, advantages])
                grads_critic = self.get_gradient_functions[1]([self.states, discounted_rewards])

                ### send trained neuralnet weights
                # weight_data = util.get_weight_with_serialized_data(actor, critic)
                # print('send trained neural-net weights {}'.format(weight_data))
                # print('actor : {} , critic : {}'.format(grads_actor, grads_critic))

                try:
                        # yield self.ws.write_message(weight_data, binary=True)
                        grads = (grads_actor, grads_critic)
                        # logging.debug('grads : {}'.format(grads))
                        # print('!!!!!!!!!!!!!grads : {}'.format(grads))
                        # yield self.ws.write_message(pickle.dumps(grads), binary=True)
                        yield self.ws.write_message(pickle.dumps(grads))
                        # print('queue.length : {}'.format(self.weight_queue.qsize()))
                except WebSocketClosedError as e:
                        # logger.warning("WS_CLOSED", "Could Not send Message: " + str(weight_data))
                        # logger.warning("WS_CLOSED", "Could Not send Message: " + 'sending gradient failed...')
                        # Send Websocket Closed Error to Paired Opponent
                        print(traceback.format_exc())
                        logger.error('WebSocketClosedError got occurred. msg : {}'.format(e))
                        self.close()

                self.states, self.actions, self.rewards = [], [], []

        def close(self):
                self.is_connection_closed = True

        def keep_alive(self):
                if self.is_connection_closed :
                        logging.debug('key_alive : disconnected')
                        self.connect()
                else:
                        logging.debug('keey_alive : send heart bit message to check ')
                        self.ws.write_message("check")

        def get_action(self, state):
                policy = actor.predict(np.reshape(state, [1, self.state_size]))[0]
                return np.random.choice(self.action_size, 1, p=policy)[0]


if __name__ == "__main__":
        localAgent = localAgent("ws://localhost:9044?local_agent_id=2", timeout=50000)
