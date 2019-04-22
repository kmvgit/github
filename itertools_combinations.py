import itertools as it

def perm(a, b):
    [[print(w) for w in sorted(k)] for k in [[''.join(sorted(h)) for h in sorted(it.combinations(a,
        i))] for i in list(range(1, b + 1))]]


a, b = input().split(' ')
perm(a,int(b))

a, b = input().split(' ')
[print(i) for i in it.combinations(a, int(b))]