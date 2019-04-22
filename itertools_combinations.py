import itertools as it

def perm(a, b):
    [[print(w) for w in k] for k in [[''.join(h) for h in it.combinations(
        sorted(a), i)] for i in range(1, b + 1)]]


a, b = input().split(' ')
perm(a,int(b))

a, b = input().split(' ')
[print(i) for i in it.combinations(a, int(b))]