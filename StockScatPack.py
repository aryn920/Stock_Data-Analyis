import datetime
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
from requests.exceptions import ConnectionError
import requests



# This function is used to extract span values from 'div' html tags from the website.
def web_content_div(web_content, tag_name, class_path):
    web_content_tags = web_content.find_all(tag_name, {'class': class_path})
    texts = []
    try:
        spans = web_content_tags[0].find_all('span')
        texts = [span.get_text() for span in spans]
    except IndexError:
        texts = []
    return texts


def web_content_li(web_content, class_path, label_class, value_class):
    web_content_tags = web_content.find_all('li', {'class': class_path})
    texts = []
    try:
        for tag in web_content_tags:
            label = tag.find('span', {'class': label_class})
            value = tag.find('span', {'class': value_class})
            if label and value:
                texts.append((label.get_text(), value.get_text()))
    except IndexError:
        texts = []
    return texts


def stock_values(stock_code):
    source_url = 'https://finance.yahoo.com/quote/' + stock_code + '/'
    try:
        resp = requests.get(source_url)
        web_content = bs(resp.text, 'html.parser')
        texts = web_content_div(web_content, 'div', 'container yf-aay0dk')
        if texts != []:
            price, change, = texts[0], texts[1]
        else:
            price, change, = [], []

        texts = web_content_li(web_content, 'yf-tx3nkj', 'label yf-tx3nkj', 'value yf-tx3nkj')
        volume = []
        if texts:
            for label, value in texts:
                if label == 'Volume':
                    volume = value
                    break

        texts = web_content_li(web_content, 'last-sm last-lg yf-tx3nkj', 'label yf-tx3nkj',
                               'value yf-tx3nkj')
        target_est = []
        if texts != []:
            for label, value in texts:
                if label == '1y Target Est':
                    target_est = value

        texts = web_content_li(web_content, 'yf-tx3nkj', 'label yf-tx3nkj', 'value yf-tx3nkj')
        PE_ratio = []
        if texts != []:
            for label, value in texts:
                if label == 'PE Ratio (TTM)':
                    PE_ratio = value

    except ConnectionError:
        price, change, volume, target_est, PE_ratio = [], [], [], [], []
    return price, change, volume, target_est, PE_ratio

Stock = ['BRK-B','GOOG','AAPL','PYPL','AMZN','FB','MSFT']

# saving all the extracted data in a csv file
while (True):
    info = []
    col = []
    time_stamp = datetime.datetime.now()
    for stock_codes in Stock:
        price, change, volume, target_est, PE_ratio = stock_values(stock_codes)
        info.append(price)
        info.extend([change])
        info.extend([volume])
        info.extend([target_est])
        info.extend([PE_ratio])

    col = [time_stamp]
    col.extend(info)
    df = pd.DataFrame(col)
    df = df.T
    df.to_csv(str(time_stamp)[0:11] + 'stock data.csv', mode ='a', header =False)
    print(col)


