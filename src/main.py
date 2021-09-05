import os
import requests
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
import json
from colorama import Fore

load_dotenv(find_dotenv())

host = 'https://' + os.getenv('HOST') +  '/iserv/app/login'
payload = '_username=' + os.getenv('USER') + '&_password=' + os.getenv('PASS')
headers = {
'User-Agent': 'Constellate Client',
'Content-Type': 'application/x-www-form-urlencoded'
}

def load():
    try:
        querystring = {'target':'/iserv/exercise?filter%5Bstatus%5D=current'}
        overview = requests.request('POST', host, headers=headers, data=payload , params=querystring)
        soup = BeautifulSoup(overview.text, 'html.parser')
        for link in soup.find_all('a'):
            target = link.get('href')
            if target.startswith('https://' + os.getenv('HOST') + '/iserv/exercise/show/'):
                extract(target)
    except (Exception, ArithmeticError) as e:
            template = Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception of type' + Fore.LIGHTBLUE_EX + ' {0} ' + Fore.RESET + 'occurred.' + Fore.LIGHTBLACK_EX + ' {1!r}'
            message = template.format(type(e).__name__, e.args)
            print (message)

def extract(url):
    try:
        id = url.replace('https://' + os.getenv('HOST') + '/iserv/exercise/show/', '')
        querystring = {'target':'/iserv/exercise/show/' + id}
        if not os.path.exists('../tasks/' + id + '.json'):
            tasks = requests.request('POST', host, headers=headers, data=payload , params=querystring)

            soup = BeautifulSoup(tasks.text, features='html.parser')
            description_html = []
            description = ""
            div = soup.find_all(class_='text-break-word p-3')
            for div in soup.find_all(class_='text-break-word p-3'):
                for p in div.find_all('p'):
                    description_html.append(p.get_text())
            for line in description_html:
                description += line

            linkarray = []

            for link in soup.find_all('a'):
                target = link.get('href')
                if target.startswith('/iserv/fs/file/'):
                    data = {"link": 'https://' + os.getenv('HOST') + target}
                    linkarray.append(data)

            table_of_time = soup.find(class_='bb0').find_all('tr')
            start = table_of_time[1].find('td').get_text()
            end = table_of_time[2].find('td').get_text()

            summary = soup.find('h1').get_text()[len('Details for '):]

            json = {"id": id}, {"title": summary}, {"description": description}, {"start": start}, {"end": end}, {"attachments": linkarray}
            write(id, json)
            endpoint(id, summary, description, start, end, linkarray)

    except (Exception, ArithmeticError) as e:
            template = Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception of type' + Fore.LIGHTBLUE_EX + ' {0} ' + Fore.RESET + 'occurred.' + Fore.LIGHTBLACK_EX + ' {1!r}'
            message = template.format(type(e).__name__, e.args)
            print (message)

def write(id, content):
    try:
        if not os.path.exists('../tasks/' + id + '.json'):
            with open('../tasks/' + id + '.json','w') as jsonFile:
                json.dump(content, jsonFile, indent=4)
            print(Fore.GREEN + 'Success' + Fore.RESET + '→ Created File: ' + id + '.json')
        else:
            print(Fore.CYAN + 'Skipping ' + Fore.RESET + '→ File ' + Fore.GREEN + id + '.json' + Fore.RESET + ' already exists.')
    except (Exception, ArithmeticError) as e:
            template = Fore.LIGHTRED_EX + 'Error ' + Fore.RESET + '→ An exception of type' + Fore.LIGHTBLUE_EX + ' {0} ' + Fore.RESET + 'occurred.' + Fore.LIGHTBLACK_EX + ' {1!r}'
            message = template.format(type(e).__name__, e.args)
            print (message)

def endpoint(id, title, description, start, end, linkarray):

    start_date = start.split(' ')
    start_date = start_date[0]
    start_date = start_date.split('/')
    start_date = start_date[2] + '-' + start_date[0] + '-' + start_date[1]

    end_date = end.split(' ')
    end_date = end_date[0]
    end_date = end_date.split('/')
    end_date_year = end_date[2]
    end_date_month = end_date[0]
    end_date_day = end_date[1]
    end_date = end_date[2] + '-' + end_date[0] + '-' + end_date[1]

    if (linkarray == []):
        data = {
            'authorization': str('demo'),
            'id': int(id),
            'title': title,
            'description': description + '<br><br>' + ' **Abgabedatum:** ' + end_date_day + '.' + end_date_month + '.' + end_date_year,
            'start-date': str(start_date),
            'end-date': str(end_date),
            'link': 'https://' + os.getenv('HOST') + '/iserv/exercise/show/' + str(id),
        }
    else:
         data = {
            'authorization': str('demo'),
            'id': int(id),
            'title': title,
            'description': description + '<br><br>' + ' **Abgabedatum:** ' + end_date_day + '.' + end_date_month + '.' + end_date_year,
            'start-date': str(start_date),
            'end-date': str(end_date),
            'link': 'https://' + os.getenv('HOST') + '/iserv/exercise/show/' + str(id),
            'attachments': linkarray
        }       
    requests.request('POST', 'https://api.nitroapp.de/v1/post', headers={'User-Agent': 'IServ', 'Content-Type': 'application/json'}, data=json.dumps(data))

        

load()
