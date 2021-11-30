import requests
from requests_html import HTMLSession

import json
import time


def get_yahoo_finance_USD_SGD_rate():
    """ Get USDSGD exchange rate from yahoo finance by scapping the website """
    url = "https://sg.finance.yahoo.com/quote/USDSGD=X/"
    try:
        session = HTMLSession()
        response = session.get(url)
    except requests.exceptions.RequestException as e:
        print(e)

    USDSGD = float(
        response.html.xpath(
            "//div[@data-reactid='28']/fin-streamer[@data-reactid='29']")[0].text)
    print(USDSGD)
    return (USDSGD)


def get_mas_USD_SGD_rate():
    """ Get USDSGD exchange rate from MAS API """
    api_link = "https://eservices.mas.gov.sg/api/action/datastore/search.json?resource_id=95932927-c8bc-4e7a-b484-68a66a24edfe&fields=usd_sgd,end_of_day&limit=1&sort=end_of_day%20desc"
    r = requests.get(api_link).json()
    while r["success"] != True:
        print("Failed to get USDSGD rate. Trying again...")
        r = requests.get(api_link).json()
    USDSGD = float(r["result"]["records"][0]["usd_sgd"])

    return USDSGD


def get_price(coin_id_param):
    """ Gets the current price of active coins from CoinGecko API """
    currencyParam = ','.join(['usd', 'sgd'])
    payload = {'ids': coin_id_param, 'vs_currencies': currencyParam}
    r = requests.get('https://api.coingecko.com/api/v3/simple/price',
                     params=payload)
    return r.json()


def get_price_all(coin_id_param):
    """ Gets the current price of all coins (including inactive ones) from CoinGecko API """
    currencyParam = ','.join(['usd', 'sgd'])
    payload = {'ids': coin_id_param, 'vs_currencies': currencyParam}
    r = requests.get('https://api.coingecko.com/api/v3/simple/price',
                     params=payload)
    return r.json()


def getHistoricalPrice(coinID, date, currency='usd'):
    #coingecko format: dd-mm-yyyy
    query_date = date[:2] + '-' + date[3:5] + '-' + date[6:]
    r = requests.get(
        'https://api.coingecko.com/api/v3/coins/{}/history?date={}&localization=false'
        .format(coinID, query_date))
    success = False
    price = 0
    if r.status_code == 404:
        return 0
    while not success:
        try:
            price = r.json()['market_data']['current_price'][currency]
            success = True
        except json.decoder.JSONDecodeError:
            print('Json decoder error! Trying again...')
            time.sleep(5)
            r = requests.get(
                'https://api.coingecko.com/api/v3/coins/{}/history?date={}&localization=false'
                .format(coinID, query_date))
    return price
