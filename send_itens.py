import os
from random import randint
from dotenv import load_dotenv
import undetected_chromedriver as uc
import firebase_admin
from firebase_admin import db, credentials
from crud import set_amazon


load_dotenv()   # Load environment variables

options = uc.ChromeOptions()
options.headless = True
driver = uc.Chrome(options=options)   # Headless browser

driver.get("https://www.amazon.com.br/gp/bestsellers/?ref_=nav_cs_bestsellers")
driver.implicitly_wait(randint(1, 3))
driver.get("https://www.amazon.com.br/gp/bestsellers/?ref_=nav_cs_bestsellers")

cred = credentials.Certificate('firebase_credentials.json')
#   Initialize Firebase app with credentials and database URL
firebase_admin.initialize_app(
    cred,
    {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
    }
)

with open('afiliate_links.txt', 'r') as file:
    links = file.readlines()
    product_info = {}

    for num, link in enumerate(links):
        last_item = db.reference('/last_item').get()
        try:
            if 'amzn' in link:
                product_info = set_amazon(link, driver)
                print(product_info)

        except Exception as e:
            with open('errors.txt', 'a') as error_file:
                error_file.write(f'Error: {e}\nLink: {link}\n\n')
            continue
        db.reference(f'/itens/{(last_item + 1)}').update(
            {
                'Link': product_info['Link'],
                'Produto': product_info['Produto'],
                'Valor': product_info['Valor'],
                'Ultimo_valor': product_info['Valor']
            }
        )
        db.reference('/last_item').set(last_item + 1)
