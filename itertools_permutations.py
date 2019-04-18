import itertools as it

def perm(a, b):
    [print(''.join(i)) for i in sorted(it.permutations(a,b))]


a, b = input().split(' ')
perm(a,int(b))