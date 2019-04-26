import re

[print(True) if len(re.findall('^[+-]?\d*\.\d+$', j)) else print(False) for j \
        in [input() for i in range(int(input()))]]
