"""Module with test task"""

import re
import datetime
import itertools

import requests
from lxml import html


def request_city(cities, question):
    """To request a city from the user."""
    while True:
        city = input(f'{question}\r\n('
                     f'{",".join(cities)})').upper()
        if city in cities:
            break
        print('You have entered incorrect data')
    return city


def get_option_directions(session, departure_city):
    """Return the options of directions."""
    url = f'http://www.flybulgarien.dk/script/getcity/2-{departure_city}'
    result = session.get(url=url).json()
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
        headers=headers).text
    return result


def format_date(dates):
    """Return the list of dates in the format 01.01.2009."""
    list_date = set(re.findall(r'\d+[,]?\d+[,]?\d+[.]?', dates))
    list_date = [pos.split(',') for pos in list_date]
    list_date = [datetime.datetime.strptime(f'{el[2]}.{el[1]}.{el[0]}',
                                            '%d.%m.%Y') for el in list_date]
    list_date.sort()
    list_date = [el.strftime('%d.%m.%Y') for el in list_date]
    return list_date


def request_date(question, list_date):
    """Request a date from the user."""
    while True:
        date = input(question)
        if date in list_date:
            break
        print('You have entered incorrect data')
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
        url=url, params=params)
    return result.text


def actual_data(date_list, date_actual):
    """Return information according to the selected date."""
    actual_list = []
    for position in date_list:
        date = position[0].xpath('.//td[2]/text()')[0].split(' ')
        date_str = datetime.datetime.strptime(
            f'{date[1]}.{date[2]}.{date[3]}', '%d.%b.%y').strftime('%d.%m.%Y')
        if date_str == date_actual:
            actual_dict = {
                'date': date_str,
                'time_from': position[0].xpath('.//td[3]/text()')[0],
                'time_to': position[0].xpath('.//td[4]/text()')[0],
                'city_from': position[0].xpath('.//td[5]/text()')[0],
                'city_to': position[0].xpath('.//td[6]/text()')[0],
                'price': position[1].xpath('.//td[2]/text()')[0][8:-4],
                'currency': position[1].xpath('.//td[2]/text()')[0][-3:]
                }
            actual_list.append(actual_dict)
    return actual_list


def combinations_flight(departure_actual, arrival_actual):
    """Return flight options according to the selected date."""
    if arrival_actual:
        combinations_list = itertools.product(departure_actual, arrival_actual)
    elif not arrival_actual:
        combinations_list = [departure_actual]
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
        duration_times1 = calculate_time(option[0]["time_from"],
                                         option[0]["time_to"],
                                         'difference')
        print(f'duration of flight: {duration_times1}')
        print(f'price: {option[0]["price"]} {option[0]["currency"]}')
        if len(option) == 2:
            print('\nComing Back')
            print(f'date of departure: {option[1]["date"]}')
            print(f'time of departure: {option[1]["time_from"]}')
            print(f'boarding time: {option[1]["time_to"]}')
            duration_times2 = calculate_time(option[1]["time_from"],
                                             option[1]["time_to"],
                                             'difference')
            print(f'duration of flight: {duration_times2}')
            print(f'price: {option[1]["price"]} {option[1]["currency"]}')
            departure_price = float(option[0]["price"])
            arrival_prace = float(option[1]["price"])
            print(
                f'\ntotal price: '
                f'{"{:.2f}".format(departure_price + arrival_prace)} '
                f'{option[1]["currency"]}')
            print(f'total time of flight:'
                  f' {calculate_time(duration_times1, duration_times2, "amount")}')
        print('**********\n')


def calculate_time(first_time, second_time, action):
    """Return the difference or sum of two time intervals."""
    first_time = datetime.datetime.strptime(first_time, '%H:%M')
    second_time = datetime.datetime.strptime(second_time, '%H:%M')
    if action == 'difference':
        result = second_time - datetime.timedelta(
            hours=first_time.hour, minutes=first_time.minute)
    elif action == 'amount':
        result = second_time + datetime.timedelta(
            hours=first_time.hour, minutes=first_time.minute)
    result = result.strftime('%H:%M')
    return result


def main():
    """To return the options for possible flights."""
    try:
        session = requests.session()
        departure_city = request_city(
            ['CPH', 'BLL', 'PDV', 'BOJ', 'SOF', 'VAR'],
            'Where do you want to fly from?')
        option = get_option_directions(session, departure_city)
        if not option:
            out_result([])
        else:
            arrival_city = request_city(
                [key for key in option], 'Where do you want to fly?')
            dates = list_dates(session, departure_city, arrival_city)
            list_date = format_date(dates)
            if not list_date:
                out_result([])
            else:
                departure_date = request_date(f"Departure date?"
                                              f"\r\n(in the format "
                                              f"01.01.2019)\r\n (available "
                                              f"dates: "
                                              f"{','.join(list_date)})",
                                              list_date)
                arrival_date = input('Choose a return date? (y\\n)')
                if arrival_date.lower() == 'y':
                    arrival_date = request_date("Return date?"
                                                "\r\n(in the format"
                                                " 01.01.2019)\r\n"
                                                "(Press enter if it"
                                                " does not matter.)"
                                                f"\r\n(available dates:"
                                                f" {','.join(list_date)})",
                                                list_date)
                else:
                    arrival_date = None
                    print('The search will be made without taking'
                          ' into account the date of return.')
                information = recuested_information(session,
                                                    departure_city,
                                                    arrival_city,
                                                    departure_date,
                                                    arrival_date)
                combinations_list = parse_data(
                    information, departure_date, arrival_date)
                out_result(combinations_list)
    except requests.exceptions.ProxyError:
        print(
            'Sorry, the service is currently unavailable.'
            '\r\nPlease try again later.')
    except requests.exceptions.ReadTimeout:
        print(
            'Unfortunately, the data was not received'
            ' because the server did not respond in time.'
            '\r\nPlease try again later.')


if __name__ == '__main__':
    main()
