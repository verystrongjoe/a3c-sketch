import tornado
from tornado.ioloop import IOLoop

def task(num):
    print('task %s' % num)

def create_task(num):
    tornado.ioloop.IOLoop.instance().add_callback(callback=lambda: task(num))

if __name__ == '__main__':
    for i in range(1,5):
        create_task(i)
    IOLoop.instance().start()