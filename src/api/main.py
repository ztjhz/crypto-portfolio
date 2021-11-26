import requests
from requests_html import HTMLSession


def get_yahoo_finance_USD_SGD_rate():
    url = "https://sg.finance.yahoo.com/quote/USDSGD=X/"
    try:
        session = HTMLSession()
        response = session.get(url)
    except requests.exceptions.RequestException as e:
        print(e)

    USDSGD = float(
        response.html.xpath(
            "//div[@data-reactid='28']/span[@data-reactid='29']")[0].text)
    return (USDSGD)


def get_mas_USD_SGD_rate():
    api_link = "https://eservices.mas.gov.sg/api/action/datastore/search.json?resource_id=95932927-c8bc-4e7a-b484-68a66a24edfe&fields=usd_sgd,end_of_day&limit=1&sort=end_of_day%20desc"
    r = requests.get(api_link).json()
    while r["success"] != True:
        print("Failed to get USDSGD rate. Trying again...")
        r = requests.get(api_link).json()
    USDSGD = float(r["result"]["records"][0]["usd_sgd"])

    return USDSGD


def get_price(coin_id_df):
    coinIDParam = ','.join(coin_id_df[coin_id_df['ACTIVE'] == True]['COIN ID'])
    currencyParam = ','.join(['usd', 'sgd'])
    payload = {'ids': coinIDParam, 'vs_currencies': currencyParam}
    r = requests.get('https://api.coingecko.com/api/v3/simple/price',
                     params=payload)
    return r.json()


def get_price_all(coin_id_df):
    coinIDParam = ','.join(coin_id_df['COIN ID'])
    currencyParam = ','.join(['usd', 'sgd'])
    payload = {'ids': coinIDParam, 'vs_currencies': currencyParam}
    r = requests.get('https://api.coingecko.com/api/v3/simple/price',
                     params=payload)
    return r.json()