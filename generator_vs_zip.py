def generator(*a):
    for i in list(range(min(len(x) for x in a))):
        yield tuple(x[i] for x in a)

a = [1,2,3,5,8,3,5,9,2,5,7,8]
b = [4,5,7,5,3,8,6,3,7,4,6,0,2]
c = [7,8,9,1,4,5,7,6,2,9,6,8,3,6,0]
d = [5,6,9,2,7,9,5,3,7,5,4,9,2,7,3]
e = [5,7,2,5,3,8,3,8,8]
h = [3,5,7,3,6,8,9,5,4,6,8]

gen = generator(a, b, c, h, d)

[print(i) for i in gen]
