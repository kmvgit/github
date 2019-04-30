import re
import collections as coll

log = 'access2.log'

def popular(reg_str, log, count_str):
    """Log file analysis"""

    dict_str = coll.defaultdict(int)
    with open(log, 'rt') as file_log:
        for line in file_log:
            try:
                str_data = reg_str.match(line).group(1)
            except:
                continue
            dict_str[str_data] += 1
    list_data = coll.Counter(dict_str).most_common(count_str)
    return list_data

print('_________________')
reg_customer = re.compile('(^(\d{1,3}.?){4})')
for line in popular(reg_customer, log, 10):
    print(line)

print('_________________')
reg_platform = re.compile('^(?:\d{1,3}.?){4}[\s\S]*? \d{3} [^"]*?"[^"]*?" "['
                          '^\(]*?\((([^\)](?!bot))*?)\)')
for line in popular(reg_platform, log, 5):
    print(line)

