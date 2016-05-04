from flask import Flask, request, render_template
from flask_googlemaps import GoogleMaps, Map
import pandas as pd
from math import ceil

app = Flask(__name__)
GoogleMaps(app)

@app.route('/')
def submission_page():
    return render_template("map_properties.html")

@app.route('/search', methods=['POST'] )
def search():
    f = pd.read_csv("https://s3.amazonaws.com/cruntar_house/prediction.csv")


    d = {}
    inputs = ['city', 'postalCode', 'bedroom', 'bathroom', 'price_min', 'price_max', 'sqrt_min', 'sqrt_max', 'lotsize_min', 'lotsize_max', 'hoa_min', 'hoa_max', 'builtyear_min', 'builtyear_max', 'maximumdayslisted']
    for input_value in inputs:
        try:
            d[input_value] = str(request.form[input_value])
            print input_value, d[input_value]
        except:
            d[input_value] = "Any"
    print len(f)
    if d['city'] != 'Any':
        try:
            f = f[f['City']==d['city']]
        except:
            pass
    if d['postalCode'] != 'Any':
        try:
            f = f[f['postalCode']==d['postalCode']]
        except:
            pass
    if d['bedroom'] != 'Any':
        try:
            f = f[f['bed']==int(d['bedroom'])]
        except:
            pass
    if d['bathroom'] != 'Any':
        try:
            f = f[f['bath']==int(d['bathroom'])]
        except:
            pass
    if d['price_min'] != 'Any':
        try:
            f = f[f['price'] >= int(d['price_min'])]
        except:
            pass
    if d['price_max'] != 'Any':
        try:
            f = f[f['price'] <= int(d['price_max'])]
        except:
            pass
    if d['sqrt_min'] != 'Any':
        try:
            f = f[f['sqrt'] >= int(d['sqrt_min'])]
        except:
            pass
    if d['sqrt_max'] != 'Any':
        try:
            f = f[f['sqrt'] <= int(d['sqrt_max'])]
        except:
            pass
    if d['lotsize_min'] != 'Any':
        try:
            f = f[f['lot_size'] >= int(d['lotsize_min'])]
        except:
            pass
    if d['lotsize_max'] != 'Any':
        try:
            f = f[f['lot_size'] <= int(d['lotsize_max'])]
        except:
            pass
    if d['hoa_min'] != 'Any':
        try:
            f = f[f['HOA'] >= int(d['hoa_min'])]
        except:
            pass
    if d['hoa_max'] != 'Any':
        try:
            f = f[f['HOA'] <= int(d['hoa_max'])]
        except:
            pass
    if d['builtyear_min'] != 'Any':
        try:
            f = f[f['built'] >= int(d['builtyear_min'])]
        except:
            pass
    if d['builtyear_max'] != 'Any':
        try:
            f = f[f['built'] <= int(d['builtyear_max'])]
        except:
            pass
    if d['maximumdayslisted'] != 'Any':
        try:
            f = f[f['on_site'] <= d['maximumdayslisted']]
        except:
            pass
    try:
        f = f[f['percent_difference'] > 0.1]
        f.sort(columns='percent_difference', ascending=False, inplace=True)
    except:
        pass
    print f.head(2)
    d = zip(f['price'], f['estimate'], f['sqft'], f['link'], f['img'], f['Latitude'], f['Longitude'])
    # only take the first 200 records
    if len(d) > 200:
        d = d[:200]
    pages = range(1, int(ceil(len(d) / 25.)+1))
    return render_template("map_properties_result.html", d=d, pages=pages)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=True)
