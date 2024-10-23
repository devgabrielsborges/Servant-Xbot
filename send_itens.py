import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import db, credentials
from crud import set_amazon

load_dotenv()   # Load environment variables

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
                product_info = set_amazon(link)
                print(product_info)

        except Exception as e:
            with open('errors.txt', 'a') as error_file:
                error_file.write(f'Error: {e}\nLink: {link}\n\n')
            continue
        db.reference(f'/itens/{last_item + 1}').update(
            {
                'Link': product_info['Link'],
                'Produto': product_info['Produto'],
                'Valor': product_info['Valor'],
                'Ultimo_valor': product_info['Valor']
            }
        )
        db.reference('/last_item').set(last_item + 1)
