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
import threading
import cartpole.util as util
import cartpole.network as network

class localAgent():
        def __init__(self, global_newtork_ip, global_newtowrk_port):
                self.actor, self.critic = network.build_model()
                util.get_gradient_with_serialized_data(actor)





