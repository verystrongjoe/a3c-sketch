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
import cartpole.config as config
import tensorflow as tf
from keras import backend as K
import gym
import numpy as np

env = gym.make(config.A3C_ENV['env_name'])

action_size = env.action_space.n
state_size = env.observation_space.shape[0]

actor, critic = network.build_model(state_size, action_size, 24, 24, True)  # declaring here is to share this between WShanlder and global agent


class localAgent():
        # def __init__(self, global_newtork_ip='localhost', global_newtowrk_port=9044, timeout=5):
        def __init__(self, url, timeout=5):
                # self.actor, self.critic = network.build_model()
                self.ws = None

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
                self.connect()
                # PeriodicCallback(self.keep_alive, 5000).start()
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
                        self.ws = yield websocket_connect(self.url)
                        # self.ws = yield websocket_connect(self.url, on_message_callback=self.cb_receive_weight)
                except Exception as e:
                        print("connection error : {0}".format(e))
                else:
                        print("connected")

                        while self.ws is None:
                                self.ws = yield websocket_connect(self.url)
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

        # save <s, a ,r> of each step
        # this is used for calculating discounted rewards
        def memory(self, state, action, reward):
                self.states.append(state)
                act = np.zeros(self.action_size)
                act[action] = 1
                self.actions.append(act)
                self.rewards.append(reward)

        # @gen.coroutine
        def run(self):
                print('run!!')
                #util.get_weight_with_serialized_data(actor, critic)
                # while True:
                #         msg = yield self.ws.read_message()
                #         print('weight : {} '.format(msg))
                #         if msg is None:
                #                 print("connection closed")
                #                 # util.set_weight_with_serialized_data(actor, critic, msg)
                #                 self.ws = None
                #                 break
                #         else:
                #                 print('msg is not null!!!!!!!')
                #                 util.set_weight_with_serialized_data(actor, critic, msg)
                #

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
                        self.ws.write_message(weight_data)
                except WebSocketClosedError:
                        # logger.warning("WS_CLOSED", "Could Not send Message: " + json.dumps(message))
                        # Send Websocket Closed Error to Paired Opponent
                        # self.send_pair_message(action="pair-closed")
                        self.close()

                self.states, self.actions, self.rewards = [], [], []


        # def keep_alive(self):
        #         # print('keep alive!!! ws : {}'.format(self.ws))
        #         if self.ws is None:
        #                 # print('keey_alive : connect')
        #                 self.connect()
        #         else:
        #                 # print('keey_alive : send msg')
        #                 self.ws.write_message("send")

        def get_action(self, state):
                policy = actor.predict(np.reshape(state, [1, self.state_size]))[0]
                return np.random.choice(self.action_size, 1, p=policy)[0]


if __name__ == "__main__":
        localAgent = localAgent("ws://localhost:9044?local_agent_id=2", timeout=5)
