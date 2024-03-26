import csv

from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = 'auto-open-links-0a3c589a5f92.json'

SPREADSHEET_ID = '1Zpeay-tdN4djcl3yrCClg3Gj3iOcZd5UjM53mHPISFg'

scopes = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
service = build('sheets', 'v4', credentials=credentials)

def append_data_from_csv(csv_file_path, sheet_name):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    range_name = f'{sheet_name}!A1'  # Append at the beginning of the chosen sheet
    request = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': data}
    )
    response = request.execute()
    print(f'Data appended to {sheet_name}:', response)




SOLD_OUT = 'Sold Out'
IN_STOCK = 'In Stock'


def index_of_pattern(pattern):
    return lambda l: [idx for idx, val in enumerate(l) if val.find(pattern) > -1][0]


def is_portion(desc):
    return any(char.isdigit() for char in desc)


def remove_currency(amount):
    return float(amount) if amount[0].isdigit() else float(amount[1:])


def clean_item(item):
    try:
        p1 = remove_currency(item[2])
        p2 = remove_currency(item[3])
        return [
            ' '.join(item[0].strip().split()),
            ' '.join(item[1].strip().split()),
            max(p1, p2),
            min(p1, p2),
            item[4]
        ]
    except Exception:
        return []


def parse_blinkit():
    with open('html/blinkit.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_container = soup.find_all(attrs={'id': 'plpListId'})
    products = list(product_container[0].children)[0]

    with open('csv/blinkit.csv', 'w', newline='', encoding='utf-8',errors = 'ignore') as csvfile:
        writer = csv.writer(csvfile)
        get_delivery_time = index_of_pattern('min')

        for product in products:
            item = list(product.stripped_strings)
            if not item:
                continue
            while item[-1] in ['ADD', '2 options']:
                item.pop()
            if item[0] == 'Out of Stock':
                item.append(SOLD_OUT)
            else:
                item.append(IN_STOCK)
            item = item[get_delivery_time(item) + 1:]
            if len(item) == 4:
                item = item[:3] + item[2:]
            item = clean_item(item)
            if item:
                writer.writerow(item)


def parse_zepto():
    with open('html/zepto.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_container = soup.find_all('a', attrs={'class': 'product-card_card__zy0gz'})

    with open('csv/zepto.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        get_offer = index_of_pattern('Off')

        for product in product_container:
            item = list(product.stripped_strings)
            if item[-1] == 'Notify':
                item[-1] = SOLD_OUT
            elif item[-1] == 'Add':
                item[-1] = IN_STOCK
            item = item[get_offer(item) + 1:]
            item = clean_item(item)
            if item:
                writer.writerow(item)


def parse_bb():
    with open('html/bb.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_container = soup.findAll('li', attrs={'class': 'PaginateItems___StyledLi2-sc-1yrbjdr-1 kUiNOF'})

    with open('csv/bb.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for product in product_container:
            item = list(product.stripped_strings)
            if item[-1] == 'Notify Me':
                item[-1] = SOLD_OUT
            elif item[-1] == 'Add':
                item[-1] = IN_STOCK
            item = item[2:]
            if len(item) > 5:
                item = item[:4] + item[5:]
            if len(item) == 4:
                item = item[:3] + item[2:]
            item = clean_item(item)
            if item:
                writer.writerow(item)


def parse_instamart():
    with open('html/instamart.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_container = soup.findAll('div', attrs={'class': 'K0-3A _30Qfj'})

    with open('csv/instamart.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for product in product_container:
            item = list(product.stripped_strings)
            if '+' in item:
                item = item[:-4]
                item.append(IN_STOCK)
            parsed_item = []
            item = [parsed_item.append(x) for x in item if x not in parsed_item and x.find('Sourced') == -1 and x.find('OFF') == -1]
            if len(parsed_item) > 5:
                if is_portion(parsed_item[1]):
                    parsed_item = [parsed_item[0]] + [' '.join(parsed_item[1:-3])] + parsed_item[-3:]
                else:
                    parsed_item = [parsed_item[0]] + [' '.join(parsed_item[2:-3])] + parsed_item[-3:]
            item = clean_item(parsed_item)
            if item:
                writer.writerow(item)


try:
    print('Scraping Blinkit...')
    parse_blinkit()
    append_data_from_csv('csv/blinkit.csv', 'Blinkit')
    print('\033[92mSuccesfully scraped Blinkit!\033[0m')
except Exception as e:
    print("\033[91mError Pasrsing Blinkit!\033[0m", e)


try:
    print('Scraping Zepto...')
    parse_zepto()
    append_data_from_csv('csv/zepto.csv', 'Zepto')
    print('\033[92mSuccesfully scraped Zepto!\033[0m')
except Exception as e:
    print("\033[91mError Pasrsing Zepto!\033[0m", e)


try:
    print('Scraping BigBasket...')
    parse_bb()
    append_data_from_csv('csv/bb.csv', 'BigBasket')
    print('\033[92mSuccesfully scraped BigBasket!\033[0m')
except Exception as e:
    print("\033[91mError Pasrsing BigBasket!\033[0m", e)


try:
    print('Scraping Instamart...')
    parse_instamart()
    append_data_from_csv('csv/instamart.csv', 'Instamart')
    print('\033[92mSuccesfully scraped Instamart!\033[0m')
except Exception as e:
    print("\033[91mError Pasrsing Instamart!\033[0m", e)


# At the end of parse_blinkit()


# At the end of parse_zepto()


# At the end of parse_bb()


# At the end of parse_instamart()

