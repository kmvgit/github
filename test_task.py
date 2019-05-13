"""Module with test task"""

import re
import datetime

import requests
from lxml import html


departure_cities = ['CPH', 'BLL', 'PDV', 'BOJ', 'SOF', 'VAR']
arrival_cities = []
proxies = {
    'http': '127.0.0.1:8888',
    'https': '127.0.0.1:8888'
}

departure_date = ''
arrival_date = ''

def request_departure_city():
    """The request of the city from where you want to fly"""

    global departure_cities
    city = input(f'Where do you want to fly from?\r\n({",".join(departure_cities)})').upper()
    if city not in departure_cities:
        print('You have entered incorrect data')
        city = request_departure_city()
    return city


def request_arrival_city():
    """The request of the city where you want to fly"""

    global arrival_cities
    city = input(f'Where do you want to fly?\r\n({",".join(arrival_cities)})').upper()
    if city not in arrival_cities:
        print('You have entered incorrect data')
        city = request_arrival_city()
    return city


def request_date(question, list_date):
    """Date request"""

    date = input(question)
    if date not in list_date:
        print('You have entered incorrect data')
        date = request_date(question, list_date)
    return date


def format_date(dates):
    """Format the date"""

    list_date = set(re.findall(r'\d+[,]?\d+[,]?\d+[.]?', dates))
    list_date = [pos.split(',') for pos in list_date]
    list_date = ['{:02}.{:02}.{}'.format(int(el[2]), int(el[1]), int(el[0]))
                 for el in list_date]
    return sorted(list_date)


def split_list(list_element, count_element):
    """Splitting the list into the
       required number of sublists"""

    element_list = []
    for index in range(0, len(list_element), count_element):
        element_list.append(list_element[index:index + count_element])
    return element_list


def actual_data(date_list, date_actual):
    """Selection of information according to the current date"""

    actual_list = []
    for position in date_list:
        date = position[0].xpath('.//td[2]/text()')[0].split(' ')
        date_str = datetime.datetime.strptime(
            f'{date[1]}.{date[2]}.{date[3]}', '%d.%b.%y').strftime('%d.%m.%Y')
        if date_str == date_actual:
            actual_dict = {}
            actual_dict['date'] = date_str
            actual_dict['time_from'] = position[0].xpath('.//td[3]/text()')[0]
            actual_dict['time_to'] = position[0].xpath('.//td[4]/text()')[0]
            actual_dict['city_from'] = position[0].xpath('.//td[5]/text()')[0]
            actual_dict['city_to'] = position[0].xpath('.//td[6]/text()')[0]
            actual_dict['price'] = position[1].xpath('.//td[2]/text()')[0][8:]
            actual_list.append(actual_dict)
    return actual_list


def combinations_flight(departure_actual, arrival_actual):
    """Making a list of possible flight combinations"""

    if arrival_actual:
        combinations_list = [
            [departure, arrival] for departure in departure_actual
            for arrival in arrival_actual]
    elif not arrival_actual:
        combinations_list = [[departure] for departure in departure_actual]
    return combinations_list


def parse_data(xml):
    """Parsing information from the site"""

    global departure_date, arrival_date
    page = html.document_fromstring(xml)
    departure_list_str1 = page.xpath(
        './/tr[starts-with(@id, "flywiz_rinf")]')
    departure_list_str2 = page.xpath(
        './/tr[starts-with(@id, "flywiz_rprc")]')
    departure_list_element = zip(departure_list_str1, departure_list_str2)
    arrival_list_str1 = page.xpath(
        './/tr[starts-with(@id, "flywiz_irinf")]')
    arrival_list_str2 = page.xpath(
        './/tr[starts-with(@id, "flywiz_irprc")]')
    arrival_list_element = zip(arrival_list_str1, arrival_list_str2)
    departure_actual = actual_data(departure_list_element, departure_date)
    arrival_actual = actual_data(arrival_list_element, arrival_date)
    combinations_list = combinations_flight(departure_actual, arrival_actual)
    return combinations_list


def duration_flight(start, finish):
    """Calculation of flight
       time in one direction"""

    start = start.split(':')
    finish = finish.split(':')
    delta_hour = int(finish[0]) - int(start[0])
    delta_minute = int(finish[1]) - int(start[1])
    if delta_minute < 0:
        delta_hour -= 1
        delta_minute = 60 + delta_minute
    delta = '{}:{}'.format(delta_hour, delta_minute)
    return delta


def amount_time(time1, time2):
    """The calculation of the total
       duration of the flight in both directions"""

    time1 = time1.split(':')
    time2 = time2.split(':')
    amount_hour = int(time1[0]) + int(time2[0])
    amount_minute = int(time1[1]) - int(time2[1])
    if amount_minute > 60:
        amount_hour += 1
        amount_minute = amount_minute - 60
    amount = '{}:{}'.format(amount_hour, amount_minute)
    return amount


def main():
    """The main function of collecting flight information"""

    global arrival_cities, departure_date, arrival_date, proxies
    session = requests.session()
    departure_city = request_departure_city()
    url = f'http://www.flybulgarien.dk/script/getcity/2-{departure_city}'
    result = session.get(url=url, proxies=proxies, verify=False).json()
    arrival_cities = [key for key in result]
    arrival_city = request_arrival_city()
    url = 'http://www.flybulgarien.dk/script/getdates/2-departure'
    direction = f'code1={departure_city}&code2={arrival_city}'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru, en;q = 0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 YaBrowser/19.4.0.2397 Yowser/2.5 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://www.flybulgarien.dk/en/',
        'Origin': 'http://www.flybulgarien.dk'
    }
    result = session.post(url=url, data=direction, headers=headers,
                          proxies=proxies, verify=False).text
    list_date = format_date(result)

    departure_date = request_date(f"Departure date?\r\n(in the format"
                                  f" 01.01.2019)\r\n(available dates:"
                                  f" {','.join(list_date)})", list_date)
    arrival_date = input('Choose a return date? (y\\n)')
    if arrival_date.lower() == 'y':
        arrival_date = request_date("Return date?\r\n(in the format"
                                    " 01.01.2019)\r\n(Press enter if it"
                                    " does not matter.)"
                                    f"\r\n(available dates:"
                                    f" {','.join(list_date)})", list_date)
    elif arrival_date.lower() == 'n':
        arrival_date = None
        print('The search will be made without taking'
              ' into account the date of return.')
    else:
        arrival_date = None
        print('You have entered an incorrect answer.\r\nThe search will'
              ' be made without taking into account the date of return.')
    url = 'https://apps.penguin.bg/fly/quote3.aspx'
    params = {
        f'{"ow" if arrival_date is None else "rt"}': '',
        'lang': 'en',
        'depdate': departure_date,
        'aptcode1': departure_city,
        'rtdate' if arrival_date is not None else "": arrival_date if
        arrival_date is not None else "",
        'aptcode2': arrival_city,
        'paxcount': '1',
        'infcount': ''
    }

    result = session.get(url=url, params=params, proxies=proxies, verify=False)
    combinations_list = parse_data(result.text)
    for option in combinations_list:
        print('**********')
        print('Going Out')
        print(f'date of departure: {option[0]["date"]}')
        print(f'time of departure: {option[0]["time_from"]}')
        print(f'boarding time: {option[0]["time_to"]}')
        duration_times1 = duration_flight(option[0]["time_from"],
                                          option[0]["time_to"])
        print(f'duration of flight: {duration_times1}')
        print(f'price: {option[0]["price"]}')
        if len(option) == 2:
            print('\nComing Back')
            print(f'date of departure: {option[1]["date"]}')
            print(f'time of departure: {option[1]["time_from"]}')
            print(f'boarding time: {option[1]["time_to"]}')
            duration_times2 = duration_flight(option[1]["time_from"],
                                              option[1]["time_to"])
            print(f'duration of flight: {duration_times2}')
            print(f'price: {option[1]["price"]}')
            print(f'\ntotal price:'
                  f' {float(option[0]["price"][:-4]) + float(option[1]["price"][:-4])}'
                  f' {option[0]["price"][-3:]}')
            print(f'total time of flight:'
                  f' {amount_time(duration_times1, duration_times2)}')
        print('**********\n')


if __name__ == '__main__':
    main()