# from multiprocessing import Process, Lock
#
# def f(i):
#     # l.acquire()
#     print('hello world', i)
#     # l.release()
#
# if __name__ == '__main__':
#     lock = Lock()
#
#     for num in range(10):
#         # Process(target=f, args=(lock, num)).start()
#         Process(target=f, args=(num,)).start()


from multiprocessing import Process, Queue, Lock
import  time
from asyncio import Queue as Queue2

# def f1(q,l):
    # while True :
    #
    #     sum = 0
    #     j = 0
    #
    #     if q.qsize() > 5:
    #
    #         while j > 10 :
    #             i = q.get()
    #             sum += i
    #             j+=1
    #             print('in f get : {}'.format(i))
    #         # while not q.empty():
    #
    #     print('in f sum~~ : {}, {}'.format(sum, j))



def f2(q):

    for i in range(1,100):
        q.put(i)
        q2.put(i)
        # prin
        print('put : {}', i)



if __name__ == '__main__':

    q = Queue()
    lock = Lock()
    q2 = Queue2()

    q2.task_done()

    p1 = Process(target=f1, args=(q,lock))
    p2 = Process(target=f2, args=(q,))

    p1.start()
    p2.start()

    print('main : ', q.qsize())


    p2.join()
    print('p2 end')
    p1.join()
    print('p1 end')