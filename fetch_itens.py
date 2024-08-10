import os
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import db, credentials
from crud import set_amazon

load_dotenv()

cred = credentials.Certificate('firebase_credentials.json')
#   Initialize Firebase app with credentials and database URL
firebase_admin.initialize_app(
    cred,
    {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
    }
)

last_item = db.reference('/last_item').get()

for item_index in range(2, last_item+1):
    product_info = {}

    try:
        product_info = set_amazon(db.reference(f'/itens/{item_index}/Link').get())
        print(product_info)
    except Exception as e:
        with open('fetch_errors.txt', 'a') as error_file:
            error_file.write(
                f'{"-"*50}\n\n\n'
                f'Index: {item_index}\n'
                f'Name: {db.reference(f"/itens/{item_index}/Produto").get()}\n'
                f'Error: {e}\nLink: {db.reference(f"/itens/{item_index}/Link").get()}\n\n'
                f'Current time: {datetime.now(timezone("Brazil/East"))}\n'
                f'{"-"*50}\n\n'
            )
        continue
    db.reference(f'/itens/{item_index}').update(
        {
            'Data': str(datetime.now(timezone("Brazil/East"))),
            'Link': product_info['Link'],
            'Produto': product_info['Produto'],
            'Valor': product_info['Valor'],
            'Ultimo_valor': product_info['Valor']
        }
    )
