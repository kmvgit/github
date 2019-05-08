import requests
import re
import datetime
from lxml import html


departure_cities = ['CPH', 'BLL', 'PDV', 'BOJ', 'SOF', 'VAR']
arrival_cities = []
proxies = {'http': 'http://127.0.0.1:8888',
           'https': 'http://127.0.0.1:8888'
           }
session = requests.session()

def request_data_get(url):
    global proxies
    global session
    result = session.get(url=url, proxies=proxies, verify=False)
    return result

def request_data_post(url, data, headers):
    global proxies
    global session
    result = session.post(url=url, data=data, headers=headers,
                          proxies=proxies, verify=False)
    return result

def request_url(departure_city, arrival_city, departure_date, arrival_date):
    url = 'https://apps.penguin.bg/fly/quote3.aspx?{}=&lang=en&depdate={' \
          '}&aptcode1={}{}&aptcode2={}&paxcount=1&infcount='.format(
                                                        'ow' if arrival_date == None else 'rt',
                                                        departure_date,
                                                        departure_city,
                                                        f'&rtdate={arrival_date}' if arrival_date != None else "",
                                                        arrival_city)
    return url

def request_departure_city():
    global departure_cities
    city = input(f'Where do you want to fly from?\r\n({",".join(departure_cities)})').upper()
    if city not in departure_cities:
        print('You have entered incorrect data')
        city = request_departure_city()
    return city

def request_arrival_city():
    global arrival_cities
    city = input(f'Where do you want to fly?\r\n({",".join(arrival_cities)})').upper()
    if city not in arrival_cities:
        print('You have entered incorrect data')
        city = request_arrival_city()
    return city

def request_date(question, list_date):
    date = input(question)
    if date not in list_date:
        print('You have entered incorrect data')
        date = request_date(question, list_date)
    return date

def format_date(dates):
    list_date = set(re.findall('\d+,\d+,\d+', dates))
    list_date = [pos.split(',') for pos in list_date]
    list_date = ['{:02}.{:02}.{}'.format(int(el[2]), int(el[1]), int(el[0]))
                 for el in list_date]
    return sorted(list_date)

def split_list(list_element, count_element):
    element_list = []
    for index in range(0, len(list_element), count_element):
        element_list.append(list_element[index:index + count_element])
    return element_list

def parse_data(xml):
    page = html.document_fromstring(xml)
    departure_list_element = page.xpath(
        './/tr[starts-with(@id, "flywiz_rinf") or starts-with(@id, "flywiz_rprc")]')
    departure_list_element = split_list(departure_list_element, 2)
    arrival_list_element = page.xpath(
        './/tr[starts-with(@id, "flywiz_irinf") or starts-with(@id, "flywiz_irprc")]')
    arrival_list_element = split_list(arrival_list_element, 2)
    for position in departure_list_element:
        date = position[0].xpath('.//td[2]/text()')[0].split(' ')
        times = datetime.datetime.strptime(f'{date[1]}.{date[2]}.{date[3]}','%d.%b.%y')
        print(times.strftime('%d.%m.%Y'))


def main():
    global arrival_cities
    departure_city = request_departure_city()
    url = f'http://www.flybulgarien.dk/script/getcity/2-{departure_city}'
    arrival_cities = [key for key in request_data_get(url).json()]
    arrival_city = request_arrival_city()
    url = 'http://www.flybulgarien.dk/script/getdates/2-departure'
    direction = f'code1={departure_city}&code2={arrival_city}'
    headers = {
        'Accept': '*/*',
        'X - Requested - With': 'XMLHttpRequest',
        'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 YaBrowser/19.4.0.2397 Yowser/2.5 Sa',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://www.flybulgarien.dk/en/',
        'Accept - Encoding': 'gzip, deflate',
        'Accept - Language': 'ru, en;q = 0.9'
    }
    dates = request_data_post(url, direction, headers).text
    list_date = format_date(dates)

    departure_date = request_date(f"Departure date?\r\n(in the format "
                                  f"01.01.2019)\r\n(available dates: {','.join(list_date)})", list_date)
    arrival_date = input('Choose a return date? (y\\n)')
    if arrival_date.lower() == 'y':
        arrival_date = request_date("Return date?\r\n(in the format 01.01.2019)\r\n(Press enter if it does not matter.)"
                                    f"\r\n(available dates: {','.join(list_date)})", list_date)
    elif arrival_date.lower() == 'n':
        arrival_date = None
        print('The search will be made without taking into account the date of return.')
    else:
        arrival_date = None
        print('You have entered an incorrect answer.\r\nThe search will be made without taking into account the date of return.')


    url = request_url(departure_city, arrival_city, departure_date, arrival_date)
    xml = request_data_get(url)
    alд_data = parse_data(xml.text)


if __name__ == '__main__':
    main()
