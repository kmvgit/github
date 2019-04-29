def is_leap(year):
    if year % 400 == 0:
        return True
    elif year % 4 == 0 and year % 100 != 0:
        return True
    #Наверное здесь не нужен else, на выходе и так будет False, если не
    # будет захода в блоки if-elif
    return False

year = int(input())
print(is_leap(year))