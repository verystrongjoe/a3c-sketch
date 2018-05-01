import threading


# def sum(low, high):
#     total = 0
#     for i in range(low, high):
#         total += i
#     print("Subthread", total)
#
#
# t = threading.Thread(target=sum, args=(1, 100000))
# t.start()
#
# print("Main Thread")

from threading import Thread
from queue import  Queue

in_queue = Queue(2)

def consumer():
    print('c waiting')
    # work = in_queue.get()
    # print('c working')
    # print('c done')
    # in_queue.task_done()


print('t start')
t = Thread(target=consumer())
print('t end')
t.start()


while True :
    in_queue.put(object())
    print('p working 1 ')
    in_queue.put(object())
    print('p working 2')
    in_queue.get()
    print('p working 3')
    in_queue.get()
    print('p working 4')
    in_queue.task_done()
    in_queue.task_done()
    in_queue.join()
    print('p done')


