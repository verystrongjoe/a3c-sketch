import keras.backend as K
import numpy as np
'''
keras.backend.function의 동작
'''
x = K.placeholder(shape=(None, 1))
w = K.variable(3)  # parameter
y = w * x
# arguments는 반드시 list로 받아야 함
# updates: tf.assign(x, new_x) 함수와 동일
# 함수가 실행될 때 마다 w 를 w-1로 대체한다
fun = K.function(inputs=[x], outputs=[y], updates = [K.update(w, w-1)])

# fun function
print(fun([np.ones((5, 1))]))
print(K.eval(w)) # output: 2

print(fun([np.ones((5, 1))]))
print(K.eval(w)) # output: 2
