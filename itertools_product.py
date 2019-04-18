import itertools as it

def decart(a, b):
    return ' '.join([str(i) for i in it.product(a, b)])


a = [int(i) for i in input().split(' ')]
b = [int(i) for i in input().split(' ')]

print(decart(a, b))