import pandas as pd
import requests
import re
import csv
import time
from bs4 import BeautifulSoup, UnicodeDammit
import os
import boto
import urllib


ACCESS_KEY = os.environ['AWS_ACCESS_KEY_ID']
SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

def get_basic_info(zipcodes, website):
    urls = []
    if website == 'ziprealty':
        for zipcode in sorted(zipcodes):
            try:
                url = 'https://www.ziprealty.com/homes-for-sale/list/sf/by-zip/%s/detailed' % zipcode
                urls.append(url)
                for i in xrange(2, 10):
                    url_later_page = url + '?pageNum=' + str(i)
                    urls.append(url_later_page)
            except:
                pass
    return urls

def scrape_img_link(img_urls):
    all_imgs_for_all_links = []
    for img in img_urls:
        parts = img.split('/')
        add_one_folder = parts[-1][-10:-8]
        add_second_folder = "_P"
        last_part = parts[-1].split('_')[0]
        img_link = '/'.join(parts[:-1]) + '/' + add_one_folder + '/' + add_second_folder + '/' + last_part
        all_imgs = []
        for i in xrange(1, 10):
            img_link = img_link + '_P0' + str(i) + '.jpg'
            r = requests.get(img_link)
            if r.status_code == 404:
                break
            else:
                all_imgs.append(img_link)
        for i in xrange(11, 21):
            img_link = img_link + '_P' + str(i) + '.jpg'
            r = requests.get(img_link)
            if r.status_code == 404:
                break
            else:
                all_imgs.append(img_link)

        all_imgs_for_all_links.append(all_imgs)
    return all_imgs_for_all_links

def scrape(urls, scrape_cols, link_class, img_class, website):
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

        detail_names = ['NA1', 'bed', 'bath', 'sqft', 'price_per_sqrt', 'CND', 'NA2', 'lot_size', 'built', 'on_site', 'NA3']

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

        col_dict['price'] = soup(class_=scrape_cols['price'])
        price_col = [item.get_text() for item in col_dict['price']]
        price_series = pd.DataFrame(price_col, columns=['price'])
        basic_data = pd.concat([basic_data, price_series], axis=1)

        links = soup(class_=link_class, href=True)
        link_list = ['https://www.%s.com%s' %(website, link['href']) for link in links]
        link_col = pd.Series(link_list, name='link')
        basic_data = pd.concat([basic_data, link_col], axis=1)

        imgs = []

        for each_div in soup.findAll('div',{'class': img_class[0]}):
            try:
                next_class = each_div.find('div', attrs={'class': img_class[1]})
                next_a = next_class.find('a', attrs={'itemprop': 'image'})
                next_itemprop = next_a.find('meta', attrs={'itemprop': 'contentUrl'})
                imgs.append(next_itemprop['content'])
            except:
                try:
                    next_class = each_div.find('div', attrs={'class': img_class[1]})
                    next_img = next_class.find('img', attrs={'alt': 'Home Photo'})
                    imgs.append(next_img['src'])
                except:
                    pass
        HOAs = []
        for link in basic_data['link']:
            html_str = requests.get(link)
            soup = BeautifulSoup(html_str.content, "html.parser")
            get_HOA_detail = soup(class_='prop-details')
            col_list = [item.get_text() for item in get_HOA_detail]
            detail = [attr.split('\n') for attr in col_list]
            HOA = detail[0][-2]
            if '(Monthly)' in HOA:
                HOAs.append(HOA.replace(' (Monthly)', ''))
            else:
                HOAs.append('0')
        # print len(basic_data), len(imgs)
        basic_data['HOA'] = HOAs
        basic_data['img'] = imgs

        whole_data = pd.concat([whole_data, basic_data], axis=0)

    return whole_data
        #details = soup.find("div", {"id": "searchCount"}).text

def clean_data(df):

    col_to_split = {'addressLocality': ['City', 'Region']}

    words_to_remove = {'bed': ['bed'],
                       'bath': ['bath'],
                       'sqft': ['sq ft', ','],
                       'price_per_sqrt': ['/ sq ft', '$', ','],
                       'lot_size': ['Lot Size', 'sq ft', ','],
                       'built': ['Built'],
                       'on_site': ['On Site', 'days'],
                       'price': ['$', ','],
                       'HOA': ['$']}

    for key in words_to_remove:
        for word in words_to_remove[key]:
            # testing
            try:
                df[key] = df[key].str.replace(word, '')
            except:
                df[key] = 0

    for col in col_to_split:
        city_region_df = df[col].str.split(' - ', expand=True)
        city_region_df.rename(columns={0:col_to_split[col][0], 1:col_to_split[col][1]}, inplace=True)
        df = pd.concat([df, city_region_df], axis=1)
        df.drop(col, axis=1, inplace=True)

    df = df.convert_objects(convert_numeric=True)
    # df[col_to_numeric] = df[col_to_numeric].astype(float)
    # try:
    #     df.drop('NA', axis=1, inplace=True)
    # except:
    #     pass

    return df

def write_to_s3(input_file, output_file):

    conn = boto.connect_s3(ACCESS_KEY, SECRET_ACCESS_KEY)

    all_buckets = [b.name for b in conn.get_all_buckets()]

    # Check if bucket exist. If exist get bucket, else create one
    bucket_name = 'cruntar_house'

    if conn.lookup(bucket_name) is None:
        b = conn.create_bucket(bucket_name, policy='public-read')
    else:
        b = conn.get_bucket(bucket_name)

    file_object = b.new_key(output_file)
    file_object.set_contents_from_filename(input_file)
    file_object.set_canned_acl('public-read')

if __name__=='__main__':
    geo_df = pd.read_csv('../../data/us_postal_codes.csv')
    geo_subset = geo_df
    # geo_subset = geo_df[geo_df['County']=='San Francisco']
    raw_zipcodes = list(geo_subset['Postal Code'])
    zipcodes = []
    for zipcode in zipcodes:
        try:
            zipcodes.append(int(zipcode))
        except:
            pass
    # zipcodes = [94102, 94103, 94104, 94105]
    # zipcodes = [94103]
    website = 'ziprealty'
    scrape_cols ={'itemprop': ['postalCode', 'addressRegion', 'addressLocality', 'streetAddress'], 'class': ['mt-10 mb-10 prop-details'], 'price': 'font-list-price font-20' }
    link_class = 'font-20 font-underline vmiddle ib mb-5'
    # img_class = 'photobox photobox--180'
    img_class = ['media__img media__img--stdmarg', 'photobox photobox--180']
    # for houses in sf on ziprealty
    # complete_url = https://www.ziprealty.com/homes-for-sale/list/sf/by-zip/94102/detailed

    print "Get URLs based on zipcodes"
    urls = get_basic_info(zipcodes, website)
    print urls
    print "Get house details from URLs and store them into dataframe..."
    main_df = scrape(urls, scrape_cols, link_class, img_class, website)
    print "house info dataframe saved, and start cleaning df"
    print main_df.head()
    clean_df = clean_data(main_df)
    final_df = clean_df.merge(geo_subset, how='left', left_on='postalCode', right_on='Postal Code')

    input_file = 'temp.csv'
    print "Save dataframe as CSV"
    final_df.to_csv(input_file)
    print "Write CSV to S3"
    write_to_s3(input_file, 'us.csv')

    print "Write json file to S3 with img links"
    # Get all imgs for each property
    print "Start scraping all img links"
    imgs = scrape_img_link(final_df['img'])
    json_df = final_df[['streetAddress', 'link', 'price']]
    json_df['imgs_to_train'] = imgs
    json_file = 'us.json'
    final_df.to_json(json_file)
    write_to_s3(json_file, json_file)
