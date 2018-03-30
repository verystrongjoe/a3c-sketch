import tensorflow as tf
from tensorflow.contrib.keras import layers
from keras.models import Sequential
from keras.layers import Dense, Activation
import pickle

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
def get_gradient_with_serialized_data(model):
    dict = {}
    for layer in model.layers:
        dict[layer.get_config()] = layer.get_weights()
    return pickle.dumps(dict)

def set_gradient_with_serialized_data(model, d):
    dict = pickle.loads(d)

    for layer_name in dict.keys():
        model.get_layer(layer_name).set_weights(dict[layer_name])

    return model

if __name__ == "__main__":

    '''
    tesing about data serializatoin
    '''
    input_x = tf.placeholder(tf.float32, [None, 10], name='input_x')
    dense1 = layers.Dense(10, activation='relu')
    y = dense1(input_x)
    weights = dense1.get_weights()
    print(weights)

    '''
    tesing about data deserializatoin
    '''

    data_string = pickle.dumps(weights)
    data_loaded = pickle.loads(data_string) #data loaded
    print(data_loaded)

    '''
    check in case of map data type
    '''
    dict = {}
    dict['a'] = 1
    dict['b'] = 2
    dict['c'] = '3'

    s =  pickle.dumps(dict)
    data_loaded = pickle.loads(s)
    print(data_loaded['a'])
