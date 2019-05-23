"""Module with test task"""

import re
import datetime
import itertools
import json
import sys
import sqlite3
import calendar

import requests
from lxml import html


def get_user_city(cities, question):
    """Return the city requested from the user."""
    while True:
        city = input(f'{question}\r\n('
                     f'{",".join(cities)})').upper()
        if city in cities:
            break
        print('You have entered incorrect data')
    return city


def get_option_departure(connect):
    """Return the options of departure."""
    with connect:
        connect = connect.cursor()
        result = set(connect.execute("SELECT DEPART_IATA FROM data"))
        result = [el[0] for el in result]
    return result


def get_option_directions(connect, field):
    """Return the options of directions."""
    with connect:
        connect = connect.cursor()
        result = set(connect.execute(
            "SELECT ARRIVE_IATA FROM data WHERE DEPART_IATA = '%(field)s'" % {
                'field': field
            }))
    result = [el[0] for el in result]
    return result


def get_user_date(question, days, name_days):
    """Return the date requested from the user."""
    while True:
        date = input(question)
        date = re.search(r'^\d\d.\d\d.\d{4}$', date)
        if date:
            date = date.group(0)
            day = str(datetime.datetime.strptime(date, '%d.%m.%Y').weekday())
            if day in days:
                return date
            print(f'Enter the date corresponding to the days of the week:'
                  f' {name_days[1:-1]}')
        else:
            print('You have entered incorrect data')


def get_days_departure(connect, depart, arrive):
    """Get possible days of departure."""
    with connect:
        connect = connect.cursor()
        result = connect.execute(
            "SELECT FLIGHT_SCHEDULE FROM data WHERE DEPART_IATA ="
            " '%(depart)s' AND ARRIVE_IATA = '%(arrive)s'" % {
                'depart': depart,
                'arrive': arrive
            }).fetchall()[0][0]
    days = [pos for pos in [
        str(day[0]) if day[1] == '+' else False for day in
        enumerate(result)] if pos]
    return days


def get_name_days_week(days):
    """Return the names of the days of the week."""
    days = [calendar.day_name[int(name)] for name in days]
    days = f"({', '.join(days)})"
    return days


def get_information_site(session, departure_city, arrival_city,
                         departure_date, arrival_date):
    """Get information from the site."""
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
    try:
        result = session.get(
            url=url, params=params).text
        return result
    except requests.exceptions.ConnectionError:
        print(
            'Sorry, the service is currently unavailable.'
            '\r\nPlease try again later.')
        sys.exit()
    except requests.exceptions.Timeout:
        print(
            'Unfortunately, the data was not received'
            ' because the server did not respond in time.'
            '\r\nPlease try again later.')
        sys.exit()


def get_data_dataset(xml, departure_date, arrival_date):
    """Return data from the dataset."""
    try:
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
        departure_actual = filter_data(departure_list_element, departure_date)
        arrival_actual = filter_data(arrival_list_element, arrival_date)
        combinations_list = get_combination_flights(departure_actual,
                                                    arrival_actual)
        return combinations_list
    except ValueError:
        print('Something went wrong. '
              'Further work with the '
              'service is impossible.')
        sys.exit()


def get_combination_flights(departure_actual, arrival_actual):
    """Return flight options according to the selected date."""
    if arrival_actual:
        combinations_list = list(itertools.product(
            departure_actual, arrival_actual))
    elif not arrival_actual:
        combinations_list = [departure_actual]
    return combinations_list


def filter_data(date_list, date_actual):
    """Return data corresponding to the current date."""
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


def output_result_user(combinations_list):
    """Output the result to the user."""
    if not combinations_list:
        print('No data found for the specified parameters')
    try:
        for option in combinations_list:
            print('**********')
            print('Going Out')
            print(f'date of departure: {option[0]["date"]}')
            print(f'time of departure: {option[0]["time_from"]}')
            print(f'boarding time: {option[0]["time_to"]}')
            duration_times1 = get_calculate_time(option[0]["time_from"],
                                                 option[0]["time_to"],
                                                 'difference')
            print(f'duration of flight: {duration_times1}')
            print(f'price: {option[0]["price"]} {option[0]["currency"]}')
            if len(option) == 2:
                print('\nComing Back')
                print(f'date of departure: {option[1]["date"]}')
                print(f'time of departure: {option[1]["time_from"]}')
                print(f'boarding time: {option[1]["time_to"]}')
                duration_times2 = get_calculate_time(option[1]["time_from"],
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
                print(f'total time of flight: '
                      f'{get_calculate_time(duration_times1, duration_times2, "amount")}')
            print('**********\n')
    except (TypeError, IndexError):
        print('Something went wrong. '
              'Further work with the '
              'service is impossible.')


def get_calculate_time(first_time, second_time, action):
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


def get_option_departure_site(session):
    """Return the options of departure."""
    url = 'http://www.flybulgarien.dk/bg/'
    try:
        result = session.get(url).text
        page = html.document_fromstring(result)
        elements = page.xpath(
            './/*[@id="departure-city"]/option[@value!=""]')
        departure_list = [element.xpath('./@value')[0] for element in
                          elements]
        return departure_list
    except requests.exceptions.ConnectionError:
        print(
            'Sorry, the service is currently unavailable.'
            '\r\nPlease try again later.')
        sys.exit()
    except requests.exceptions.Timeout:
        print(
            'Unfortunately, the data was not received'
            ' because the server did not respond in time.'
            '\r\nPlease try again later.')
        sys.exit()


def get_option_directions_site(session, departure_city):
    """Return the options of directions."""
    url = f'http://www.flybulgarien.dk/script/getcity/2-{departure_city}'
    try:
        result = session.get(url=url).json()
        directions_list = [key for key in result]
        return directions_list
    except requests.exceptions.ConnectionError:
        print(
            'Sorry, the service is currently unavailable.'
            '\r\nPlease try again later.')
        sys.exit()
    except requests.exceptions.Timeout:
        print(
            'Unfortunately, the data was not received'
            ' because the server did not respond in time.'
            '\r\nPlease try again later.')
        sys.exit()
    except json.JSONDecodeError:
        print('Incorrect data were obtained.')
        sys.exit()


def get_option_date_site(session, departure_city, arrival_city):
    """Return date options from the site."""
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
    try:
        result = session.post(
            url=url, data=f'code1={departure_city}&code2={arrival_city}',
            headers=headers).text
        return result
    except requests.exceptions.ConnectionError:
        print(
            'Sorry, the service is currently unavailable.'
            '\r\nPlease try again later.')
        sys.exit()
    except requests.exceptions.Timeout:
        print(
            'Unfortunately, the data was not received'
            ' because the server did not respond in time.'
            '\r\nPlease try again later.')
        sys.exit()


def change_date_format(dates):
    """Return the list of dates in the format 01.01.2009."""
    try:
        list_date = set(re.findall(r'\d+[,]?\d+[,]?\d+[.]?', dates))
        list_date = [pos.split(',') for pos in list_date]
        list_date = [datetime.datetime.strptime(
            f'{el[2]}.{el[1]}.{el[0]}', '%d.%m.%Y') for el in list_date]
        list_date.sort()
        days = sorted(list(set(el.weekday() for el in list_date)))
        date_string = '-------'
        for pos in days:
            date_string = '{:-<7}'.format(f"{date_string[:pos]}+")
        return date_string
    except TypeError:
        print('Something went wrong. '
              'Further work with the '
              'service is impossible.')
        sys.exit()


def write_data_database(connect, option_d, option_a, dates):
    """Write data to the database."""
    with connect:
        connect = connect.cursor()
        connect.execute("INSERT OR REPLACE INTO data (Route_ID, "
                        "DEPART_IATA, "
                        "ARRIVE_IATA, FLIGHT_SCHEDULE)"
                        " VALUES (NULL, '%(depart)s', "
                        "'%(arrive)s', '%(flight)s')" %
                        {'depart': option_d,
                         'arrive': option_a,
                         'flight': dates
                        })


def get_data_site(session, connect):
    """Get data from the site."""
    options_d = get_option_departure_site(session)
    for option_d in options_d:
        options_a = get_option_directions_site(session, option_d)
        if options_a:
            for option_a in options_a:
                dates = get_option_date_site(session, option_d, option_a)
                if len(dates) > 2:
                    dates = change_date_format(dates)
                    write_data_database(connect, option_d, option_a, dates)


def get_user_data(connect, session):
    """Return data received from the user."""
    departure_cities = get_option_departure(connect)
    if not departure_cities:
        get_data_site(session, connect)
        departure_cities = get_option_departure(connect)
    departure_city = get_user_city(departure_cities,
                                   'Where do you want to fly from?')
    arrival_cities = get_option_directions(connect, departure_city)
    arrival_city = get_user_city(
        arrival_cities, 'Where do you want to fly?')
    days = get_days_departure(connect, departure_city, arrival_city)
    name_days = get_name_days_week(days)
    print(f'Possible departure days: {name_days}')
    departure_date = get_user_date(
        f"Departure date?\r\n(in the format 01.01.2019)",
        days, name_days)
    arrival_date = input('Choose a return date? (y\\n)')
    if arrival_date.lower() == 'y':
        arrival_date = get_user_date(
            "Return date?\r\n(in the format 01.01.2019)",
            days, name_days)
    else:
        arrival_date = None
        print(
            'The search will be made without taking into account'
            ' the date of return.')
    return departure_city, arrival_city, departure_date, arrival_date


def main():
    """Main function."""
    connect = sqlite3.connect('test_task.db')
    session = requests.Session()
    departure_city, arrival_city, departure_date, arrival_date = get_user_data(
        connect, session)
    information = get_information_site(session, departure_city, arrival_city,
                                       departure_date, arrival_date)
    combinations_list = get_data_dataset(
        information, departure_date, arrival_date)
    output_result_user(combinations_list)


def create_database():
    """Create a database."""
    connect = sqlite3.connect('test_task.db')
    with connect:
        connect.execute("""CREATE TABLE IF NOT EXISTS data (
            Route_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            DEPART_IATA TEXT(3),
            ARRIVE_IATA TEXT(3),
            FLIGHT_SCHEDULE TEXT(7)
            )""")


if __name__ == '__main__':
    create_database()
    main()
