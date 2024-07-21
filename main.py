import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import db, credentials
from funcs import set_amazon

load_dotenv()   # Load environment variables

cred = credentials.Certificate('firebase_credentials.json')
#   Initialize Firebase app with credentials and database URL
firebase_admin.initialize_app(
    cred,
    {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
    }
)

#   Open file with links
with open('links.txt', 'r') as file:
    links = file.readlines()
    product_info = {}

    #   Loop for each link in file
    for link_index, link in enumerate(links):
        index = db.reference('/last_item').get()
        try:
            #   Check if link is from Amazon
            if 'amzn' in link:
                product_info = set_amazon(link)
                print(product_info)

        except Exception as e:
            #   Write error in file
            with open('errors.txt', 'a') as error_file:
                error_file.write(
                    f'Error: {e}\nLink: {link}\n'
                    f'Index: {link_index + 1}\n\n'
                )
            continue
        #   Update database with product info
        db.reference(f'/itens/{index + 1}').update(
            {
                'Link': product_info['Link'],
                'Produto': product_info['Produto'],
                'Valor': product_info['Valor'],
                'Ultimo_valor': product_info['Valor']
            }
        )
        #   Update last item index
        db.reference('/last_item').set(index + 1)
