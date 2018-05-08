from keras.layers import Dense, Input
from keras.models import Model
# from keras.optimizers import Adam
from keras import backend as K
from cartpole.optimizer import SGD_custom
import cartpole.config as config

'''
This nework is for a3c network which can be either global or local network.
This network is consist of two network, advantage and policy network.
'''
# _state_size = 20
# _action_size = 20
# _hidden1 = 20
# _hidden2 = 20
def build_model(state_size, action_size, hidden1, hidden2, verbose=False) :
    state = Input(batch_shape=(None, state_size))
    shared = Dense(hidden1, input_dim=state_size, activation='relu')(state)

    action_hidden = Dense(hidden2, activation='relu')(shared)
    policy_value = Dense(action_size, activation='softmax')(action_hidden)

    value_hidden = Dense(hidden2, activation='relu')(shared)
    state_value = Dense(1, activation='linear')(value_hidden)

    actor = Model(inputs=state, outputs=policy_value)
    critic = Model(inputs=state, outputs=state_value)

    # custom optimizer
    # opt_c = SGD_custom(lr=config.A3C_ENV['critic_lr'])
    # opt_a = SGD_custom(lr=config.A3C_ENV['actor_lr'])

    # critic.compile(optimizer=opt_c)
    # actor.compile(optimizer=opt_a)

    if verbose:
        actor.summary()
        critic.summary()

    return actor, critic

def train_critic_with_grads(critic,grads):
    grad_input = [K.placeholder(shape=K.int_shape(w), dtype=K.dtype(w)) for w in critic.trainable_weights]
    opt_c = SGD_custom(lr=config.A3C_ENV['critic_lr'])
    updates = opt_c.get_updates(grad_input, critic.trainable_weights)
    train = K.function([grad_input, critic.trainable_weights], updates=updates)
    return train

def train_actor_with_grads(actor, grads):
    grad_input = [K.placeholder(shape=K.int_shape(w), dtype=K.dtype(w)) for w in critic.trainable_weights]
    opt_a = SGD_custom(lr=config.A3C_ENV['actor_lr'])
    updates = opt_a.get_updates(grad_input, actor.trainable_weights)
    train = K.function([grad_input, actor.trainable_weights], updates=updates)
    return train

def get_gradients_from_actor(actor):
    """
    get gradients from actor model
    :param actor:
    :param actor_lr:
    :param action_size:
    :return:
    """
    # action = K.placeholder(shape=(None, config.A3C_ENV['action_size']))
    action = K.placeholder(shape=(None, 2))
    advantages = K.placeholder(shape=(None,))
    policy = actor.output
    good_prob = K.sum(action * policy, axis=1)
    eligibility = K.log(good_prob + 1e-10) * K.stop_gradient(advantages)
    loss = -K.sum(eligibility)
    entropy = K.sum(policy * K.log(policy + 1e-10), axis=1)
    actor_loss = loss + 0.01 * entropy

    optimizer = SGD_custom(lr=config.A3C_ENV['actor_lr'])
    grad_ops = optimizer.get_gradients(actor_loss, actor.trainable_weights)

    return K.function([actor.input, action, advantages], grad_ops)

def get_gradients_from_critic(critic):
    """
    get gradients from critic model
    :param critic:
    :param critic_lr:
    :return:
    """
    discounted_reward = K.placeholder(shape=(None, ))
    value = critic.output
    critic_loss = K.mean(K.square(discounted_reward - value))
    optimizer = SGD_custom(lr=config.A3C_ENV['critic_lr'])
    grad_ops = optimizer.get_gradients(critic_loss, critic.trainable_weights)

    return K.function([critic.input, discounted_reward], grad_ops)

def save_model(actor, critic, name):
    actor.save_weights(name + "_actor.h5")
    critic.save_weights(name + "_critic.h5")

def load_model(actor, critic, name):
    actor.actor.load_weights(name + "_actor.h5")
    critic.critic.load_weights(name + "_critic.h5")