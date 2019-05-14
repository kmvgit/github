"""Module with test task"""

import re
import datetime

import requests
from lxml import html


def request_city(cities, question):
    """To request a city from the user."""

    city = input(f'{question}\r\n('
                 f'{",".join(cities)})').upper()
    if city not in cities:
        print('You have entered incorrect data')
        city = request_city(cities, question)
    return city


def option_fight(session, departure_city):
    """Return the options of directions."""

    url = f'http://www.flybulgarien.dk/script/getcity/2-{departure_city}'
    result = session.get(url=url, proxies=None, verify=False).json()
    return result


def list_dates(session, departure_city, arrival_city):
    """Return date variants."""

    url = 'http://www.flybulgarien.dk/script/getdates/2-departure'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru, en;q = 0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/73.0.3683.86 YaBrowser/19.4.0.2397'
                      ' Yowser/2.5 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://www.flybulgarien.dk/en/',
        'Origin': 'http://www.flybulgarien.dk'
    }
    result = session.post(
        url=url, data=f'code1={departure_city}&code2={arrival_city}',
        headers=headers, proxies=None, verify=False).text
    return result


def format_date(dates):
    """Return the list of dates in the format 01.01.2009."""

    list_date = set(re.findall(r'\d+[,]?\d+[,]?\d+[.]?', dates))
    list_date = [pos.split(',') for pos in list_date]
    list_date.sort(key=lambda x: x[2])
    list_date.sort(key=lambda x: x[1])
    list_date = ['{:02}.{:02}.{}'.format(int(el[2]), int(el[1]), int(el[0]))
                 for el in list_date]
    return list_date


def request_date(question, list_date):
    """Request a date from the user."""

    date = input(question)
    if date not in list_date:
        print('You have entered incorrect data')
        date = request_date(question, list_date)
    return date


def recuested_information(session, departure_city, arrival_city,
                          departure_date, arrival_date):
    """Get information from the server."""

    url = 'https://apps.penguin.bg/fly/quote3.aspx'
    params = {
        f'{"ow" if arrival_date is None else "rt"}': '',
        'lang': 'en',
        'depdate': departure_date,
        'aptcode1': departure_city,
        'rtdate' if arrival_date is not None else "":
            arrival_date if arrival_date is not None else "",
        'aptcode2': arrival_city,
        'paxcount': '1',
        'infcount': ''
    }
    result = session.get(
        url=url, params=params, proxies=None, verify=False)
    return result.text


def actual_data(date_list, date_actual):
    """Return information according to the selected date."""

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
    """Return flight options according to the selected date."""

    if arrival_actual:
        combinations_list = [
            [departure, arrival] for departure in departure_actual
            for arrival in arrival_actual]
    elif not arrival_actual:
        combinations_list = [[departure] for departure in departure_actual]
    return combinations_list


def parse_data(xml, departure_date, arrival_date):
    """Parse the data and return possible combinations of flights."""

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


def out_result(combinations_list):
    """Display information to the user."""

    if not combinations_list:
        print('No data found for the specified parameters')
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
            departure_price = float(option[0]["price"][:-4])
            arrival_prace = float(option[1]["price"][:-4])
            print(
                f'\ntotal price: {departure_price + arrival_prace}'
                f' {option[0]["price"][-3:]}')
            print(f'total time of flight:'
                  f' {amount_time(duration_times1, duration_times2)}')
        print('**********\n')


def duration_flight(start, finish):
    """Calculate the difference between two time points."""

    start = start.split(':')
    finish = finish.split(':')
    if int(finish[0]) < int(start[0]):
        delta_hour = int(finish[0]) + 24 - int(start[0])
    else:
        delta_hour = int(finish[0]) - int(start[0])
    delta_minute = int(finish[1]) - int(start[1])
    if delta_minute < 0:
        delta_hour -= 1
        delta_minute = 60 + delta_minute
    delta = '{}:{:02}'.format(delta_hour, delta_minute)
    return delta


def amount_time(time1, time2):
    """Calculate the sum of two time intervals."""

    time1 = time1.split(':')
    time2 = time2.split(':')
    amount_hour = int(time1[0]) + int(time2[0])
    amount_minute = int(time1[1]) - int(time2[1])
    if amount_minute > 60:
        amount_hour += 1
        amount_minute = amount_minute - 60
    amount = '{}:{:02}'.format(amount_hour, amount_minute)
    return amount


def main():
    """To return the options for possible flights."""

    session = requests.session()
    departure_city = request_city(
        ['CPH', 'BLL', 'PDV', 'BOJ', 'SOF', 'VAR'],
        'Where do you want to fly from?')
    option = option_fight(session, departure_city)
    arrival_city = request_city(
        [key for key in option], 'Where do you want to fly?')
    dates = list_dates(session, departure_city, arrival_city)
    list_date = format_date(dates)
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
    else:
        arrival_date = None
        print('The search will be made without taking'
              ' into account the date of return.')
    information = recuested_information(session,
                                        departure_city,
                                        arrival_city,
                                        departure_date, arrival_date)
    combinations_list = parse_data(information, departure_date, arrival_date)
    out_result(combinations_list)


if __name__ == '__main__':
    main()
