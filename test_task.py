"""Module with test task"""

import re
import datetime
import itertools
import json
import sys
import sqlite3

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


def get_option_departure():
    """Return the options of departure."""
    result = set(data_base.execute("SELECT DEPART_IATA FROM data"))
    result = [el[0] for el in result]
    return result


def get_option_directions(field):
    """Return the options of directions."""
    result = set(data_base.execute(
        "SELECT ARRIVE_IATA FROM data WHERE DEPART_IATA = '%(field)s'" % {
            'field': field
        }))
    result = [el[0] for el in result]
    return result


def main():
    """To return the options for possible flights."""
    departure_cities = get_option_departure()
    departure_city = request_city(departure_cities,
                                  'Where do you want to fly from?')
    arrival_cities = get_option_directions(departure_city)








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

def format_date(dates):
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


def write_data_database(option_d, option_a, dates):
    """Write data to the database."""
    data_base.execute("SELECT DEPART_IATA, ARRIVE_IATA, FLIGHT_SCHEDULE "
                 "FROM data WHERE DEPART_IATA = '%(depart)s' AND ARRIVE_IATA "
                 "= '%(arrive)s' AND FLIGHT_SCHEDULE = '%(flight)s'" % {
                     'depart': option_d,
                     'arrive': option_a,
                     'flight': dates
                 })
    if not data_base.fetchall():
        data_base.execute("INSERT INTO data (Route_ID, DEPART_IATA, "
                     "ARRIVE_IATA, FLIGHT_SCHEDULE)"
                     " VALUES (NULL, '%(depart)s', "
                     "'%(arrive)s', '%(flight)s')" % {
                         'depart': option_d,
                         'arrive': option_a,
                         'flight': dates
                     })
        connect.commit()


def get_data_site():
    """Get data from the site."""
    session = requests.session()
    options_d = get_option_departure_site(session)
    for option_d in options_d:
        options_a = get_option_directions_site(session, option_d)
        if options_a:
            for option_a in options_a:
                dates = list_dates(session, option_d, option_a)
                if len(dates) > 2:
                    dates = format_date(dates)
                    write_data_database(option_d, option_a, dates)
    connect.close()


def connect_database():
    """Return the database cursor."""
    connect = sqlite3.connect('c:/github/test_task.db')
    data_base = connect.cursor()
    data_base.execute("""CREATE TABLE IF NOT EXISTS data (
    Route_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    DEPART_IATA TEXT(3),
    ARRIVE_IATA TEXT(3),
    FLIGHT_SCHEDULE TEXT(7)
    )""")
    return data_base, connect


if __name__ == '__main__':
    data_base, connect = connect_database()
    #get_data_site()
    main()
