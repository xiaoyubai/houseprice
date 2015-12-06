import pandas as pd
import requests
import re
import csv
import time
from bs4 import BeautifulSoup, UnicodeDammit
import os

def get_basic_info(zipcodes, website):
    urls = []
    if website == 'ziprealty':
        for zipcode in sorted(zipcodes):
            print zipcode
            urls.append('https://www.ziprealty.com/homes-for-sale/list/sf/by-zip/%s/detailed' % zipcode)
    return urls

def scrape(urls, scrape_cols, link_class, website):
    whole_data = pd.DataFrame()
    for webpage in urls:
        html_str = requests.get(webpage)
        soup = BeautifulSoup(html_str.content, "html.parser")

        col_dict = {}
        basic_data = pd.DataFrame()
        for col in scrape_cols['itemprop']:
            col_dict[col] = soup(itemprop=col)
            col_list = [item.get_text() for item in col_dict[col]]
            col_series = pd.Series(col_list, name=col)
            basic_data = pd.concat([basic_data, col_series], axis = 1)

        detail_names = ['NA', 'bed', 'bath', 'sqft', 'price_per_sqrt', 'CND', 'NA', 'lot_size', 'built', 'on_site', 'NA']

        for col in scrape_cols['class']:
            col_dict[col] = soup(class_=col)
            col_list = [item.get_text() for item in col_dict[col]]
            detail = [attr.split('\n') for attr in col_list]
            for item in detail:
                if all("bed" not in s for s in item):
                    item.insert(1, 'N/Abed')
                if all("bath" not in s for s in item):
                    item.insert(2, 'N/Abath')
            col_series = pd.DataFrame(detail, columns=detail_names)
            basic_data = pd.concat([basic_data, col_series], axis = 1)

        links = soup(class_=link_class, href=True)
        link_list = ['https://www.%s.com%s' %(website, link['href']) for link in links]
        link_col = pd.Series(link_list, name='link')
        basic_data = pd.concat([basic_data, link_col], axis=1)

        whole_data = pd.concat([whole_data, basic_data], axis=0)

    return whole_data
        #details = soup.find("div", {"id": "searchCount"}).text

def clean_data(df):
    words_to_remove = {'bed': 'bed',
                       'bath': 'bath',
                       'sqft': 'sq ft',
                       'price_per_sqrt': '/ sq ft',
                       'lot_size': 'Lot Size',
                       'lot_size': 'sq ft',
                       'built': 'Built',
                       'on_site': 'On Site'}
    for word in words_to_remove:
        df[word] = df[word].str.replace(words_to_remove[word], '')
    df.drop('NA', axis=1, inplace=True)
    return df

if __name__=='__main__':
    #zipcodes = [94102, 94103, 94104, 94105, 94107, 94108, 94109, 94110, 94111, 94112, 94114, 94115, 94116, 94117, 94118, 94121, 94122, 94123, 94124, 94127, 94131, 94132, 94133, 94134, 94158]
    zipcodes = [94102]
    website = 'ziprealty'
    scrape_cols ={'itemprop': ['postalCode', 'addressRegion', 'addressLocality', 'streetAddress'], 'class': ['mt-10 mb-10 prop-details'] }
    link_class = 'font-20 font-underline vmiddle ib mb-5'
    # for houses in sf on ziprealty
    # complete_url = https://www.ziprealty.com/homes-for-sale/list/sf/by-zip/94102/detailed
    urls = get_basic_info(zipcodes, website)
    main_df = scrape(urls, scrape_cols, link_class, website)
    clean_df = clean_data(main_df)
    print clean_df
