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

# import threading
import cartpole.util as util
import cartpole.network as network
from tornado.ioloop import IOLoop, PeriodicCallback
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

env = gym.make(config.A3C_ENV['env_name'])

action_size = env.action_space.n
state_size = env.observation_space.shape[0]

actor, critic = network.build_model(state_size, action_size, 24, 24, True)  # declaring here is to share this between WShanlder and global agent


class localAgent():

        def send_message(self, action, **data):
                """Sends the message to the connected client
                """
                message = {
                        "action": action,
                        "data": data
                }
                try:
                        self.write_message(json.dumps(message))
                except WebSocketClosedError:
                        logger.warning("WS_CLOSED", "Could Not send Message: " + json.dumps(message))
                        # Send Websocket Closed Error to Paired Opponent
                        self.send_pair_message(action="pair-closed")
                        self.close()

        # def __init__(self, global_newtork_ip='localhost', global_newtowrk_port=9044, timeout=5):
        def __init__(self, url, timeout=5):
                # self.actor, self.critic = network.build_model()
                self.ws = None
                self.is_connection_closed = False

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

                self.ioloop = IOLoop.instance()

                print('1')
                self.connect()
                print('2')

                # PeriodicCallback(self.keep_alive, 2000).start()

                print('3')
                self.ioloop.start()

        @gen.coroutine
        def cb_receive_weight(self, weight):
                print('we get the gradient from server : {}'.format(weight))
                util.set_weight_with_serialized_data(actor, critic, weight)

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
        def connect(self):
                print("trying to connect")
                try:
                        self.ws = yield websocket_connect(self.url, connect_timeout=9977999)
                        # self.ws = yield websocket_connect(self.url, on_message_callback=self.cb_receive_weight)
                except Exception as e:
                        print("connection error : {}".format(e))
                else:
                        print("connected")

                        while self.ws is None:
                                self.ws = yield websocket_connect(self.url)
                        self.run()

        @gen.coroutine
        def get_weight_from_global_network(self):
                print('trying to get message from global network!!')

                while True:
                        if self.is_connection_closed is True:
                                self.connect()
                        else:
                                break
                print('finished to check the connection and send msg to request weight from server!!')
                self.ws.write_message('send')

                while True:

                        try:
                                response = yield self.ws.read_message(callback=self.cb_receive_weight)
                        except StreamClosedError:
                                self._abort()

                        # result = future.result(timeout)  # Wait for the result with a timeout
                        #TODO:  http://masnun.com/2015/11/20/python-asyncio-future-task-and-the-event-loop.html
                        #TODO:  http://www.tornadoweb.org/en/stable/concurrent.html
                        #TODO:  https://www.youtube.com/watch?v=IqoYVfoetFg
                        #TODO:  https://www.youtube.com/watch?v=SkETonolR3U

                        if response.done() :
                                print('weight of global network : {} '.format(f.result()))
                                # util.set_weight_with_serialized_data()
                                break
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


        def run(self):
                print('run!!')

                while True:
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
                                        print("episode: ", self.episode, "/ score : ", score)
                                        self.train_episode(score != 500)
                                        break
                        if self.episode % 3 == 0:
                                self.get_weight_from_global_network()


        # update policy network and value network every episode
        def train_episode(self, done):
                print('train_episode')
                discounted_rewards = self.discount_rewards(self.rewards, done)

                values = critic.predict(np.array(self.states))
                values = np.reshape(values, len(values))

                advantages = discounted_rewards - values

                self.optimizer[0]([self.states, self.actions, advantages])
                self.optimizer[1]([self.states, discounted_rewards])

                ### send trained neuralnet weights
                weight_data = util.get_weight_with_serialized_data(actor, critic)
                print('send trained neural-net weights {}'.format(weight_data))

                try:
                        self.ws.write_message(weight_data, binary=True)
                except WebSocketClosedError:
                        logger.warning("WS_CLOSED", "Could Not send Message: " + weight_data)
                        # Send Websocket Closed Error to Paired Opponent
                        self.close()

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

        def get_action(self, state):
                policy = actor.predict(np.reshape(state, [1, self.state_size]))[0]
                return np.random.choice(self.action_size, 1, p=policy)[0]



if __name__ == "__main__":
        localAgent = localAgent("ws://localhost:9044?local_agent_id=2", timeout=50000)
