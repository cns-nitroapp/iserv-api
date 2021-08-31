import os
import requests
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup

load_dotenv(find_dotenv())

def load():
    url = 'https://' + os.getenv('HOST') +  '/iserv/app/login'
    querystring = {'target':'/iserv/exercise?filter%5Bstatus%5D=past'}
    payload = '_username=' + os.getenv('USER') + '&_password=' + os.getenv('PASS')
    headers = {
    'User-Agent': 'Constellate Client',
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    answer = requests.request('POST', url, headers=headers, data=payload , params=querystring)
    soup = BeautifulSoup(answer.text, 'html.parser')
    for link in soup.find_all('a'):
        target = link.get('href')
        if target.startswith('https://' + os.getenv('HOST') + '/iserv/exercise/show/'):
            print(target)

    return answer

load()