import os
import requests
from bs4 import BeautifulSoup

NUM_COUNTRIES = 137
n = 1
urls = []

for n in range(NUM_COUNTRIES):
    urls.append(join('https://global.essentialmeds.org/dashboard/countries/',n))

output_directory = 'HTML Files New'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    filename = os.path.join(output_directory, f'{url.split("//")[-1]}.html')

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(soup.prettify()))