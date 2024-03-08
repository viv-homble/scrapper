import requests
from bs4 import BeautifulSoup
import csv


SOLD_OUT = 'Sold Out'
IN_STOCK = 'In Stock'


def index_of_pattern(pattern):
    return lambda l: [idx for idx, val in enumerate(l) if val.find(pattern) > -1][0]


def is_portion(desc):
    return any(char.isdigit() for char in desc)


def parse_blinkit():
    with open('html/blinkit.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_container = soup.find_all(attrs={'id': 'plpListId'})
    products = list(product_container[0].children)[0]

    with open('csv/blinkit.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        get_delivery_time = index_of_pattern('min')

        for product in products:
            item = list(product.stripped_strings)
            while item[-1] in ['ADD', '2 options']:
                item.pop()
            if item[0] == 'Out of Stock':
                item.append(SOLD_OUT)
            else:
                item.append(IN_STOCK)
            item = item[get_delivery_time(item) + 1:]
            if len(item) == 4:
                item = item[:3] + item[2:]
            writer.writerow(item)


def parse_zepto():
    with open('html/zepto.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_container = soup.find_all('a', attrs={'class': 'product-card_card__zy0gz'})

    with open('csv/zepto.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        get_offer = index_of_pattern('Off')

        for product in product_container:
            item = list(product.stripped_strings)
            if item[-1] == 'Notify':
                item[-1] = SOLD_OUT
            elif item[-1] == 'Add':
                item[-1] = IN_STOCK
            item = item[get_offer(item) + 1:]
            writer.writerow(item)


def parse_bb():
    with open('html/bb.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_container = soup.findAll('li', attrs={'class': 'PaginateItems___StyledLi2-sc-1yrbjdr-1 kUiNOF'})

    with open('csv/bb.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for product in product_container:
            item = list(product.stripped_strings)
            if item[-1] == 'Notify Me':
                item[-1] = SOLD_OUT
            elif item[-1] == 'Add':
                item[-1] = IN_STOCK
            item = item[3:]
            if len(item) > 5:
                item = item[:4] + item[5:]
            if len(item) == 4:
                item = item[:3] + item[2:]
            writer.writerow(item)


def parse_instamart():
    with open('html/instamart.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_container = soup.findAll('div', attrs={'class': 'K0-3A _30Qfj'})

    with open('csv/instamart.csv', 'a', newline='', encoding='utf-8') as csvfile:
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
            writer.writerow(parsed_item)


try:
    print('Scraping Blinkit...')
    parse_blinkit()
    print('\033[92mSuccesfully scraped Blinkit!\033[0m')
except Exception as e:
    print("\033[91mError Pasrsing Blinkit!\033[0m", e)


try:
    print('Scraping Zepto...')
    parse_zepto()
    print('\033[92mSuccesfully scraped Zepto!\033[0m')
except Exception as e:
    print("\033[91mError Pasrsing Zepto!\033[0m", e)


try:
    print('Scraping BigBasket...')
    parse_bb()
    print('\033[92mSuccesfully scraped BigBasket!\033[0m')
except Exception as e:
    print("\033[91mError Pasrsing BigBasket!\033[0m", e)


try:
    print('Scraping Instamart...')
    parse_instamart()
    print('\033[92mSuccesfully scraped Instamart!\033[0m')
except Exception as e:
    print("\033[91mError Pasrsing Instamart!\033[0m", e)
