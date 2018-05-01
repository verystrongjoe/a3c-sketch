'''
keras optimizer 동작 원리
A3C에서 asynchronous 하게 update 할 때, (1) local agent는 gradient를 전달하고
(2) global agent는 gradient를 받아서 update 하도록 구성하기 위해 필요
'''
# 준비물
import keras
from keras import backend as K
from keras.layers import Input, Dense
from keras.models import Model
# from keras_optimizer import *
from keras.legacy import interfaces

import numpy as np

from keras.optimizers import SGD

class SGD_custom(SGD):
    """Stochastic gradient descent optimizer.

    Includes support for momentum,
    learning rate decay, and Nesterov momentum.

    # Arguments
        lr: float >= 0. Learning rate.
        momentum: float >= 0. Parameter that accelerates SGD
            in the relevant direction and dampens oscillations.
        decay: float >= 0. Learning rate decay over each update.
        nesterov: boolean. Whether to apply Nesterov momentum.
    """
    @interfaces.legacy_get_updates_support
    def get_updates(self, grads, params):
        self.updates = [K.update_add(self.iterations, 1)]

        lr = self.lr
        if self.initial_decay > 0:
            lr *= (1. / (1. + self.decay * K.cast(self.iterations,
                                                  K.dtype(self.decay))))
        # momentum
        shapes = [K.int_shape(p) for p in params]
        moments = [K.zeros(shape) for shape in shapes]
        self.weights = [self.iterations] + moments
        for p, g, m in zip(params, grads, moments):
            v = self.momentum * m - lr * g  # velocity
            self.updates.append(K.update(m, v))

            if self.nesterov:
                new_p = p + self.momentum * v - lr * g
            else:
                new_p = p + v

            # Apply constraints.
            if getattr(p, 'constraint', None) is not None:
                new_p = p.constraint(new_p)

            self.updates.append(K.update(p, new_p))
        return self.updates

if __name__ == "__main__" :

    '''
    A3C에 필요한 아래의 두 가지에 대한 간단한 예제
    (1) 'updates' (gradient)를 numpy array로 받아오는 예제: (1-2) 이용
    (2) numpy array 형태의 updates를 이용해 파라미터를 업데이트 하는 예제: (2) 이용
    '''
    # local model
    x = Input(shape=(10,))
    y = Dense(5, activation='relu')(x)
    y = Dense(1, activation='linear')(y)
    model = Model(x, y)
    model.compile(optimizer='sgd', loss='mse')

    X = np.random.normal(size=(32, 10))
    Y = np.random.normal(size=(32, 1))

    # (1-2) 'gradient'를 numpy array로 받아오는 예제: 성공
    '''update를 value 로 받아와서 업데이트 하려 했으나 실패...
    gradient를 value 로 받아와서 업데이트 하는 방식으로 다시 시도'''
    y_true = K.placeholder(shape=(None, 1))
    loss = K.mean(model.loss_functions[0](y_true, model.output))
    grad_ops = model.optimizer.get_gradients(loss=loss, params=model.trainable_weights)
    fun = K.function([model.input, y_true], grad_ops)
    grad = fun([X, Y])
    # print(grad)


    # (2) numpy array 형태의 updates 를 이용해 파라미터를 업데이트 하는 예제
    # global model
    x = Input(shape=(10,))
    y = Dense(5, activation='relu')(x)
    y = Dense(1, activation='linear')(y)
    model1 = Model(x, y)
    opt = SGD_custom() # apply_gradient 방식의 custom optimizer
    model1.compile(optimizer=opt, loss='mse')

    # make gradient placeholder
    grad_input = [K.placeholder(shape=K.int_shape(w), dtype=K.dtype(w)) for w in model.trainable_weights]
    # global model update function
    update_ops = model1.optimizer.get_updates(grads=grad_input,
                                              params=model1.trainable_weights)
    # define keras function
    fun = K.function(inputs=grad_input,
                     outputs=model1.trainable_weights,
                     updates=model1.optimizer.updates)
    # value로 받은 gradient로 update 하는 함수
    # output으로 나오는 trainable_weights를 통해 모델이 학습되는 것을 확인 가능
    fun(grad)

    # cf) compare updates and gradient
    y_true = K.placeholder(shape=(None, 1))
    loss = K.mean(model.loss_functions[0](y_true, model.output))
    updates = model.optimizer.get_updates(loss=loss, params=model.trainable_weights)
    grad = model.optimizer.get_gradients(loss=loss, params=model.trainable_weights)
    fun_grad = K.function(inputs=[model.input, y_true],
                          outputs=grad)
    fun_updates = K.function(inputs=[model.input, y_true],
                             outputs=updates)
    v_grad = fun_grad([X, Y])
    v_updates = fun_updates([X, Y])

    print(len(v_grad))
    print(len(v_updates))

    # for v in v_grad:
    #     print(v.shape)
    #
    # print('  ')
    # for v in v_updates:
    #     print(v.shape)
    #
    # # v_grad[0] * 0.1 (learning rate) = v_updates[1]
    print(v_grad[0])
    print(v_updates[1])