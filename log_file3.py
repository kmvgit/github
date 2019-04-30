import timeit

setup = """
import re
import collections as coll

def list_fun(reg_str, log):


    dict_str = coll.defaultdict(int)
    with open(log, 'rt') as file_log:
        for line in file_log:
            try:
                str_data = reg_str.match(line).group(1)
            except:
                continue
            dict_str[str_data] += 1
    list_data = [line[0] for line in coll.Counter(dict_str).most_common()]
    return list_data

def filt_fun(list_data, count_str, filt = None):
    list_pos = [line for line in list_data if filt not in line]
    return list_pos[:count_str]

log = 'access2.log'
reg_platform = re.compile('^(?:\d{1,3}.?){4}[\s\S]*? \d{3} [^"]*?"[^"]*?" "['
                          '^\(]*?\(([^\)]*?)\)')

list_data = list_fun(reg_platform, log)
list_pos = list(filter(lambda pos: 'bot' not in pos, list_data))[:5]
for line in list_pos:
    print(line)
"""

time_code = timeit.Timer(setup = setup)
for val in time_code.repeat(10):
    print(val)
