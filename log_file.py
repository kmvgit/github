import re
import collections as coll

# 10 клиентов посетившие большее количество страниц
def popular_customer(reg_str, log, count_str):
    dict_str = coll.defaultdict(int)
    with open(log, 'rt') as file_log:
        for line in file_log:
            try:
                customer_ip = reg_str.match(line).group(0)
            except:
                continue
            dict_str[customer_ip] += 1
    list_ip = coll.Counter(dict_str).most_common(count_str)
    return list_ip

# 5 самых популярных платформ
def popular_platform(reg_str, log, count_str):
    dict_str = coll.defaultdict(int)
    with open(log, 'rt') as file_log:
        for line in file_log:
            try:
                platform_name = reg_str.match(line).group(1)
            except:
                continue
            if 'bot' not in platform_name.lower():
                dict_str[platform_name] += 1
    list_platform = coll.Counter(dict_str).most_common(count_str)
    return list_platform

log = 'access2.log'

print("_________________")
reg_customer = re.compile('^(\d{1,3}.?){4}')
for line_ip in popular_customer(reg_customer, log, 10):
    print(line_ip)

print('_________________')
reg_platform = re.compile('^(?:\d{1,3}.?){4}[\s\S]*? \d{3} [^"]*?"[^"]*?" "[^\(]*?\((['
                                  '^\)]*?)\)')
for line_platform in popular_platform(reg_platform, log, 5):
    print(line_platform)
