from keras.layers import Dense, Input
from keras.models import Model
# from keras.optimizers import Adam
from keras import backend as K
from cartpole.optimizer import SGD_custom

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

    if verbose:
        actor.summary()
        critic.summary()

    return actor, critic


# make loss function for Value approximation
def critic_optimizer(critic, critic_learning_rate):
    discounted_reward = K.placeholder(shape=(None,))

    value = critic.output
    loss = K.mean(K.square(discounted_reward - value))

    optimizer = SGD_custom(lr=critic_learning_rate)
    update = optimizer.get_updates(critic.trainable_weights, [], loss)
    train = K.function([critic.input, discounted_reward], [], updates=update)
    return train

def actor_optimizer(actor, actor_learning_rate, action_size):
    action = K.placeholder(shape=(None, action_size))
    advantages = K.placeholder(shape=(None,))

    policy = actor.output

    good_prob = K.sum(action*policy, axis=1)
    eligibility = K.log(good_prob + 1e-10) * K.stop_gradient(advantages)
    loss = -K.sum(eligibility)

    entropy = K.sum(policy * K.log(policy + 1e-10), axis=1)

    actor_loss = loss + 0.01 * entropy

    optimizer = SGD_custom(lr=actor_learning_rate)
    updates = optimizer.get_updates(actor.trainable_weights, [], actor_loss)
    train = K.function([actor.input, action, advantages], [], updates=updates)
    return train


def get_gradients_from_actor(actor, actor_lr, action_size):
    action = K.placeholder(shape=(None, action_size))
    advantages = K.placeholder(shape=(None,))

    policy = actor.output

    good_prob = K.sum(action * policy, axis=1)
    eligibility = K.log(good_prob + 1e-10) * K.stop_gradient(advantages)
    loss = -K.sum(eligibility)

    entropy = K.sum(policy * K.log(policy + 1e-10), axis=1)

    actor_loss = loss + 0.01 * entropy

    optimizer = SGD_custom(lr=actor_lr)

    # updates = optimizer.get_updates(self.actor.trainable_weights, [], actor_loss)
    # train = K.function([self.actor.input, action, advantages], [], updates=updates)

    return optimizer.get_gradients(actor_loss, actor.trainable_weights)

def get_gradients_from_critic(critic, critic_lr):
    discounted_reward = K.placeholder(shape=(None, ))

    value = critic.output

    actor_loss = K.mean(K.square(discounted_reward - value))

    optimizer = SGD_custom(lr=critic_lr)
    # updates = optimizer.get_updates(self.critic.trainable_weights, [], actor_loss)
    # train = K.function([self.critic.input, discounted_reward], [], updates=updates)

    return optimizer.get_gradients(actor_loss, critic.trainable_weights)

def save_model(actor, critic, name):
    actor.save_weights(name + "_actor.h5")
    critic.save_weights(name + "_critic.h5")

def load_model(actor, critic, name):
    actor.actor.load_weights(name + "_actor.h5")
    critic.critic.load_weights(name + "_critic.h5")