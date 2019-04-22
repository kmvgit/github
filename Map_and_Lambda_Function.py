cube = lambda x: x**3

def fibon(n):
    if n in [0,1]:
        return n
    elif n > 0:
        return fibon(n-1) + fibon(n-2)
    elif n < 0:
        return fibon(n+2) - fibon(n+1)

if __name__ == '__main__':
    try:
        n = int(input())
        print(list(map(fibon, range(n + 1) if n > 0
            else range(n, 1))))
        list_fib_cub = list(map(cube, list(map(fibon, range(n + 1) if n > 0
            else range(n, 1)))))
        print(list_fib_cub)
    except ValueError:
        print('Необходимо ввести любое число')


