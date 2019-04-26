import re

# 10 клиентов посетившие большее количество страниц
client = dict()
p = re.compile('^(\d{1,3}.?){4}')
for line in open('access2.log', 'rt'):
    try:
        ip_client = p.match(line).group(0)
    except:
        continue
    else:
        if ip_client in client:
            client[ip_client] += 1
        else:
            client.update({ip_client: 1})

print([id for id in sorted(client.items(), key = lambda item: item[1],
                              reverse = True)][:10])

# 5 самых популярных платформ
platform = dict()
p = re.compile('^(?:\d{1,3}.?){4}[\s\S]*? \d{3} [^"]*?"[^"]*?" "[^\(]*?\((['
               '^\)]*?)\)')
for line in open('access2.log', 'rt'):
    try:
        platform_name = p.match(line).group(1)
    except:
        continue
    else:
        if platform_name in platform:
            platform[platform_name] += 1
        else:
            platform.update({platform_name: 1})
print([id for id in sorted(platform.items(), key = lambda item: item[1],
                              reverse = True) if 'bot' not in id[0].lower()][:5])