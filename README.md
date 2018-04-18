# a3c multiprocessing version

## Introduction
This is a just simple sketch code for you to build your own a3c model based on this source code. 
For this, I converted from a basic cartpole a3c source from [here](https://github.com/rlcode/reinforcement-learning/blob/master/2-cartpole/5-a3c/cartpole_a3c.py) to its multi processing version.

You can run global agent at first then you can ran one or more local agents.
If you want local agents to run in other computer, you can do it. Because each process can communicate with websocket protocol. Instead, you set give a ip address and port of its global agent when you initiate local agent class. This is the very first application that needs to be updated and added many features.

## How to run

### Global Agent
```
run cartpole/globalAgent.py
```

### Local Agent
```
run cartpole/localAgent.py
```
## Architecture
![archi](http://cfile27.uf.tistory.com/image/2225DE4C58A334B62D6E18)

 
## Reference
[a3c architecture](http://ishuca.tistory.com/400) 


[cartpole source](https://github.com/rlcode/reinforcement-learning/blob/master/2-cartpole/5-a3c/cartpole_a3c.py)


[tornado](http://tornadoweb.org)
