import re
import fire
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

# TODO: Criar funções para demais sites, respectivamente
# TODO: Escrever documentação das funções


def set_amazon(url: str) -> dict:
    """set_amazon Returns a dict with url, product and price

    Args:
        url (str): Url of product

    Returns:
        dict: Url, Product, Price
    """
    html_body = requests.get(url).content
    soup = bs(html_body, 'html.parser')
    print("ajdb\n")

    price_search = soup.find('span', class_='a-offscreen')
    price = re.findall(re.compile(r'R\$(\d+.\d+)'), price_search.text)[0]

    name = soup.find('span', id='productTitle').get_text().strip()
    return {
        'Link': url, 'Produto': name, 'Valor': float(price.replace(',', '.'))
    }

def get_link_amazon(url: str) -> str:
    driver = uc.Chrome()
    driver.get(url)



if __name__ == '__main__':
    fire.Fire()
