import requests
import os

os.environ['HTTP_PROXY'] = 'http://localhost:8888'
os.environ['HTTPS_PROXY'] = 'https://localhost:8888'
os.environ['CURL_CA_BUNDLE'] = ''

s = requests.session()
g = s.get('https://yandex.ru?ggg=ggg').text
