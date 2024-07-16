import re
import requests
from bs4 import BeautifulSoup as bs


def set_amazon(url: str):
    html_body = requests.get(url).content
    soup = bs(html_body, 'html.parser')
    price_search = soup.find('span', class_='a-offscreen')
    price = re.findall(re.compile(r'R\$(\d+\.\d+)'), price_search.text)[0]
    name = soup.find('span', id='productTitle').get_text()

    return {
        'Link': url,
        'Produto': name,
        'Valor': float(price.replace(',', '.'))
    }
