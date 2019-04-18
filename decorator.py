import time

def decorator(arg):
    def decor(f):
        def wrapper(a, b):
            start = time.time()
            print(f'Время старта выполнения функции: {time.strftime("%H:%M:%S", time.localtime())}')
            print(f(a, b) * arg)
            finish = time.time()
            print(f'Время окончания выполнения функции {time.strftime("%H:%M:%S", time.localtime())}')
            if finish - start < 1.0:
                print(f'Время выполнения функции составило менее 1 секунды')
            else:
                print(f'Время выполнения функции составило {finish - start} секунд')
        return wrapper
    return decor


@decorator(5)
def fun(a, b):
    return a + b

fun(10, 7)