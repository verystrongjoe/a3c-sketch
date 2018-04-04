import tensorflow as tf
from tensorflow.contrib.keras import layers
from keras.models import Sequential
from keras.layers import Dense, Activation
import pickle
import threading
from copy import deepcopy


def get_model_for_test() :
    model = Sequential()
    model.add(Dense(12, input_dim=8, init='uniform', activation='relu'))
    model.add(Dense(8, init='uniform', activation='relu'))
    model.add(Dense(1, init='uniform', activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

# get weight
#  - https://stackoverflow.com/questions/43715047/keras-2-x-get-weights-of-layer/43856966#43856966
# set weight
#  - https://stackoverflow.com/questions/47183159/how-to-set-weights-in-keras-with-a-numpy-array
def get_weight_with_serialized_data(model_actor, model_critic):

    dict_pair = [{},{}]

    # dict_pair.append({})
    # dict_pair.append({})

    # dict_pair['actor'] = {}
    # dict_pair['critic'] = {}

    for layer in model_actor.layers:
        # dict_pair['actor'][layer] = layer.get_weights()
        dict_pair[0][layer] = layer.get_weights()
    for layer in model_critic.layers:
        # dict_pair['critic'][layer] = layer.get_weights()
        dict_pair[1][layer] = layer.get_weights()

    # dc = copy.deepcopy(dict_pair)

    # json_actor = model_actor.to_json()
    # json_critic = model_critic.to_json()

    # d = pickle.dumps(dict_pair)

    model_actor_weight = model_actor.get_weights()
    model_critic_weight = model_critic.get_weights()



    # return model_actor_weight, model_critic_weight
    return pickle.dumps((model_actor_weight, model_critic_weight))
    # return d

def set_weight_with_serialized_data(model_actor, model_critic, d):
    dict_pair = pickle.loads(d)

    # print(dict_pair)

    # for layer_name in dict_pair['actor'].keys():
    # for layer_name in dict_pair[0].keys():
    #     model_actor.get_layer(layer_name).set_weights(dict_pair[0][layer_name])
    #
    # # for layer_name in dict_pair['critic'].keys():
    # for layer_name in dict_pair[1].keys():
    #     model_critic.get_layer(layer_name).set_weights(dict_pair[1][layer_name])
    model_actor.set_weights(dict_pair[0])
    model_critic.set_weights(dict_pair[1])

    return model_actor, model_critic

if __name__ == "__main__":

    actor = get_model_for_test()
    critic = get_model_for_test()

    w = get_weight_with_serialized_data(actor, critic)

    set_weight_with_serialized_data(actor,critic, w)

    # pass

    '''
    tesing about data serialization
    '''
    input_x = tf.placeholder(tf.float32, [None, 10], name='input_x')
    dense1 = layers.Dense(10, activation='relu')
    y = dense1(input_x)
    weights = dense1.get_weights()
    # print(weights)

    '''
    tesing about data deserializatoin
    '''

    data_string = pickle.dumps(weights)

    # print('serialized.......................')
    # print(data_string)
    # print('serialized.......................')


    data_loaded = pickle.loads(data_string) #data loaded
    # print(data_loaded)

    '''
    check in case of map data type
    '''

    # dict_pair = []
    # dict_pair.append({})
    # dict_pair.append({})
    #
    # dict_pair[0]['a'] = 1
    # dict_pair[0]['b'] = 2
    # dict_pair[0]['c'] = '3'
    #
    # dict_pair[1]['a'] = 1
    # dict_pair[1]['b'] = 2
    # dict_pair[1]['c'] = '3'
    #
    # s = pickle.dumps(dict_pair)
    # data_loaded = pickle.loads(s)
    # print(data_loaded)
    #
    # for layer_name in data_loaded[0].keys():
    #     print(layer_name)
    #
    # for layer_name in dict_pair[1].keys():
    #     print(layer_name)