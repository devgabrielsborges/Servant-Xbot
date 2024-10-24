import re
import fire
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs


def set_amazon(url: str, driver: uc.driver) -> dict:
    """set_amazon Returns a dict with url, product and price

    Args:
        driver (object):
        url (str): Url of product

    Returns:
        dict: Url, Product, Price
    """
    driver.get(url)
    html_body = driver.page_source
    soup = bs(html_body, 'html.parser')

    price_search = soup.find('span', class_='a-offscreen')
    price = re.findall(re.compile(r'R\$(\d+.\d+)'), price_search.text)[0]

    name = soup.find('span', id='productTitle').get_text().strip()
    return {
        'Link': url, 'Produto': name, 'Valor': float(price.replace(',', '.'))
    }


if __name__ == '__main__':
    fire.Fire()
