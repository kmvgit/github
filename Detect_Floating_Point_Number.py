import re

reg_float = '^[+-]?\d*\.\d+$'
count_in = int(input())
list_in = [input() for number_str in range(count_in)]
list_out = [True if len(re.findall(reg_float, str_in)) else False for str_in in list_in]

for str_out in list_out:
        print(str_out)