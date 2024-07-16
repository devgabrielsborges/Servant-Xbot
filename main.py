import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import db, credentials
from funcs import set_amazon

load_dotenv()

cred = credentials.Certificate('firebase_credentials.json')
firebase_admin.initialize_app(
    cred,
    {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
    }
)

with open('links.txt', 'r') as file:
    links = file.readlines()
    product_info = {}

    for link in links:
        index = db.reference('/last_item').get()
        try:
            if 'amzn' in link:
                product_info = set_amazon(link)
                print(product_info)

        except Exception as e:
            with open('errors.txt', 'a') as error_file:
                error_file.write(f'Error: {e}\nLink: {link}\n\n')
            continue
        db.reference(f'/itens_amazon/{index + 1}').update(
            {
                'Link': product_info['Link'],
                'Produto': product_info['Produto'],
                'Valor': product_info['Valor']
            }
        )
        db.reference('/last_item').set(index + 1)
