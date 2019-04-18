f = [12,13,24,25,56,23,45,67,78,56,34]
d = {'a': 'aa', 'b':'bb', 'c':'cc', 'e':''}

# Принимает словарь, меняет местами ключи со значениями и возвращает новый
# словарь или возвращает  словарь с информацией об ошибке.
def update_dict(d):
    if isinstance(d, dict) and not '' in d.values():
        return {v:k for k, v in d.items()}
    return {'error':'Не возможно поменять местами ключи со значениями'}

print(update_dict(d))

# Возвращает квадраты элементов списка.
def spis_square(f):
    return [x**2 for x in f]

print(spis_square(f))

# Возвращает каждый второй элемент списка.
def spis_even(f):
    return [y for x, y in enumerate(f,1) if x % 2 == 0]

print(spis_even(f))

# Возвращает квадраты четных элементов на нечетных позициях.
def spis_element(f):
    return [y**2 for x, y in enumerate(f,1) if y % 2 == 0 and x % 2 != 0]

print(spis_element(f))