def wrapper(f):
    def fun(l):
        # complete the function
        l_new = []
        for n in l:
            l_new.append('+91 ' + n[len(n)-10:][:5] + ' ' + n[len(n)-10:][5:])
        f(l_new)
    return fun

@wrapper
def sort_phone(l):
    print(*sorted(l), sep='\n')

if __name__ == '__main__':
    l = [input() for _ in range(int(input()))]
    sort_phone(l)