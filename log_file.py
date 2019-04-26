import re

client = dict()
p = re.compile('^(\d{1,3}.?){4}')
for line in open('access2.log', 'rt'):
    ip_client = p.match(line).group(0)
    if ip_client in client:
        client[ip_client] += 1
    else:
        client.update({ip_client: 1})

print([id for id in sorted(client.items(), key = lambda item: item[1],
                              reverse = True)][:10])
