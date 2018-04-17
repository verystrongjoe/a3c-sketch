from tornado import gen, ioloop

@gen.coroutine
def func():
    print('func started')
    yield gen.moment
    print('func done')

@gen.coroutine
def func2():
    print('func2 started')
    yield gen.moment
    print('func2 done')

@gen.coroutine
def first():
    for i in range(2):
        ioloop.IOLoop.current().spawn_callback(func)

    ioloop.IOLoop.current().spawn_callback(func2)
    yield gen.sleep(1)

ioloop.IOLoop.current().run_sync(first)