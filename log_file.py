import re

class log_file:
    def __init__(self, log):
        self.dict_str = dict()
        self.file_log = open(log, 'rt')

    # 10 клиентов посетившие большее количество страниц
    def popular_customer(self, count_str):
        self.dict_str.clear()
        self.file_log.seek(0)
        self.reg_customer = re.compile('^(\d{1,3}.?){4}')
        for line in self.file_log:
            try:
                self.customer_ip = self.reg_customer.match(line).group(0)
            except:
                continue
            else:
                if self.customer_ip in self.dict_str:
                    self.dict_str[self.customer_ip] += 1
                else:
                    self.dict_str.update({self.customer_ip: 1})
        self.list_ip = [id for id in sorted(self.dict_str.items(),
                                            key = lambda item: item[1],
                                            reverse = True)][:count_str]
        return self.list_ip

    # 5 самых популярных платформ
    def popular_platform(self, count_str):
        self.dict_str.clear()
        self.file_log.seek(0)
        self.reg_platform = re.compile('^(?:\d{1,3}.?){4}[\s\S]*? \d{3} [^"]*?"[^"]*?" "[^\(]*?\((['
               '^\)]*?)\)')
        for line in self.file_log:
            try:
                self.platform_name = self.reg_platform.match(line).group(1)
            except:
                continue
            else:
                if self.platform_name in self.dict_str:
                    self.dict_str[self.platform_name] += 1
                else:
                    self.dict_str.update({self.platform_name: 1})
        self.list_platform =[id for id in sorted(self.dict_str.items(),
                                            key = lambda item: item[1],
                                            reverse = True) if 'bot' not in id[0].lower()][:count_str]
        return self.list_platform


result = log_file('access2.log')



print("_________________")
for line_ip in result.popular_customer(10):
    print(line_ip)

print('_________________')
for line_platform in result.popular_platform(5):
    print(line_platform)
