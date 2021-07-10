import requests
from bs4 import BeautifulSoup
from plyer import notification
import time

result = requests.get('https://www.mohfw.gov.in/').text  # convert website into html
obj = BeautifulSoup(result, 'html.parser')
obj.encode('utf-8')
total_case = obj.find('li', {'class': 'bg-blue'}).get_text().strip()


# print(total_case)

def tellme(tellme_title, cases):
    notification.notify(title=tellme_title, message=cases, timeout=5)


while True:
    tellme("Total cases of corona in india", total_case)
    time.sleep(3)
