import requests
import lxml.html
import re

def request_data(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                  'image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 YaBrowser/19.4.0.2397 Yowser/2.5 Safari/537.36',
        'Referer': 'http://www.flybulgarien.dk/en/',
        'Upgrade-Insecure-Requests': '1',
        'Host': 'www.flybulgarien.dk',
        'Connection': 'keep-alive'
    }
    proxies = {'http': 'http://127.0.0.1:8888',
               'https': 'http://127.0.0.1:8888'
               }
    session = requests.session()
    #result = session.get(url='http://www.flybulgarien.dk/en/',
     #headers=headers, proxies=proxies)
    #result = session.get(url=url, headers=headers, proxies=proxies)
    url = 'https://apps.penguin.bg/fly/quote3.aspx?ow=&lang=en&depdate=26.06.2019&aptcode1=CPH&aptcode2=BOJ&paxcount=1&infcount='
    result = session.get(url=url, proxies=proxies, verify=False)
    return result

def query_string_fun(departure_city, arrival_city, departure_date, arrival_date):
    query_string = ['http://www.flybulgarien.dk/en/search?', 'lang=2&',
                    f'departure-city={departure_city}&', f'arrival-city={arrival_city}&',
                    'reserve-type=&', f'departure-date={departure_date}&',
                    f'arrival-date={arrival_date}&', 'adults-children=0&search=Search']
    return ''.join(query_string)

def request_city(question):
    cities = ['CPH', 'BLL', 'PDV', 'BOJ', 'SOF', 'VAR']
    city = input(question).upper()
    if city not in cities:
        print('You have entered incorrect data')
        city = request_city(question)
    return city

def request_date(question):
    date = input(question)
    date_format = re.match('^(\d\d.){2}\d{4}$', date)
    if date_format == None and date != '':
        print('You have entered incorrect data')
        date = request_date(question)
    return date



def main():
    departure_city = request_city("Where do you want to fly from?\r\n(CPH, BLL, PDV, BOJ, SOF, VAR)")
    arrival_city = request_city("Where do you want to fly?\r\n(CPH, BLL, PDV, BOJ, SOF, VAR)")
    departure_date = request_date("Departure date?\r\n(in the format 01.01.2019)")
    arrival_date = request_date("Return date?\r\n(in the format 01.01.2019)\r\n(Press enter if it does not matter.)")

    query_string = query_string_fun(departure_city, arrival_city,
                                    departure_date, arrival_date)
    text = request_data(query_string)
    print(text.text)


if __name__ == '__main__':
    main()
