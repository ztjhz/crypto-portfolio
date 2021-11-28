""" Archive of all old functions """


def retify(data):
    """ retify errors """
    import datetime
    start_date = datetime.date(year=2021, month=11, day=9)
    end_date = datetime.date(year=2021, month=11, day=28)
    current_date = start_date

    record_df = data.getRecordDF()
    while current_date != end_date:
        d = current_date.strftime('%d/%m/%Y')
        print(d)
        # eth_price = getHistoricalPrice("ethereum", d, 'sgd')
        # cro_price = getHistoricalPrice("crypto-com-chain", d, 'sgd')
        # amount = 82.4189907 * (cro_price - eth_price)

        # record_df.loc[d, "PORTFOLIO VALUE"] += amount
        # record_df.loc[d, "TOTAL P/L"] += amount

        totalDeposited = record_df.loc[d, "TOTAL DEPOSITED"]
        totalPL = record_df.loc[d, "TOTAL P/L"]
        record_df.loc[d, "% P/L"] = (totalPL / totalDeposited) * 100
        current_date += datetime.timedelta(days=1)
    print(record_df.tail(10))


'''
# add transaction function for updateRecord function
def add_tx(portfolio_dict, coin, quantity):
    if coin not in portfolio_dict:
        portfolio_dict[coin] = quantity
    else:
        portfolio_dict[coin] += quantity

# Get CoinGecko Price Data for updateRecord function
def getCoinGeckoPrice(coin_id, date: int):
    if coin_id == 'fanscoin':
        return 0
    price = 0
    r = requests.get('https://api.coingecko.com/api/v3/coins/{}/history?date={}&localization=false'.format(coin_id, formatDate(date)))
    success = False
    while not success:
        try:
            price = r.json()['market_data']['current_price']['sgd']
            success = True
        except json.decoder.JSONDecodeError:
            print('Json decoder error! Trying again...', coin_id, date)
            time.sleep(5)
            r = requests.get('https://api.coingecko.com/api/v3/coins/{}/history?date={}&localization=false'.format(coin_id, formatDate(date)))

    return price

# Generate old record data from transaction history
def updateRecord():
    coin_dict = {"ADA": "cardano", "BTC": "bitcoin", "CRO": "crypto-com-chain", "DOT": "polkadot", "ENJ": "enjincoin", "ETH": "ethereum", "LINK": "chainlink", "VET": "vechain", "ZIL": "zilliqa", "SLP": "small-love-potion", "BNB": "binancecoin", "SWAP": "trustswap", "INJ": "injective-protocol", "YF-DAI": "yfdai-finance", "SYNC": "sync-network", 'STX': 'blockstack', 'REN': 'republic-protocol', 'XRP': 'ripple', 'XTZ': 'tezos', 'MOON': 'moonswap', 'NEO': 'neo', 'GAS': 'gas', 'FC': 'fanscoin'}
    start_date = datetime.date(year=2020,month=8,day=1)
    end_date = datetime.date(year=2020,month=9,day=30)
    current_date = start_date
    portfolio_dict = {}
    record_dict = {}
    total_deposited = 0
    total_withdrawn = 0

    while current_date != end_date:
        portfolio_value = 0
        current_date_int = int(current_date.strftime('%d%m%y'))
        print(current_date_int)
        for i, row in tx_df[tx_df['DATE'] == current_date_int].iterrows():
            type = row['TYPE']
            coin = row['COIN']
            quantity = row['QUANTITY']
            
            if coin not in coin_dict:
                x = input(f'Enter the coin id of {coin}: ')
                coin_dict[coin] = x

            price = getCoinGeckoPrice(coin_dict[coin], current_date_int)
        
            if type == 'WITHDRAW':
                total_withdrawn += abs(quantity * price)
                
            add_tx(portfolio_dict, coin, quantity)

        if current_date_int in deposit_df['DATE'].values:
            for index, r in deposit_df[deposit_df['DATE'] == current_date_int].iterrows():
                total_deposited += r['AMOUNT']
            
        for c, q in portfolio_dict.items():
            p = getCoinGeckoPrice(coin_dict[c], current_date_int)
            portfolio_value += p * q

        total_PL = total_withdrawn + portfolio_value - total_deposited
        percentage_PL = (total_PL / total_deposited) * 100

        record_dict[current_date_int] = {'TOTAL DEPOSITED': total_deposited, 'TOTAL WITHDRAWN': total_withdrawn, 'PORTFOLIO VALUE': portfolio_value, 'TOTAL P/L': total_PL, '% P/L': percentage_PL}

        current_date += datetime.timedelta(days=1)
    
    df = pd.DataFrame(record_dict).transpose()
    print(df)
    writer = pd.ExcelWriter('record.xlsx')
    df.to_excel(writer,'Record')
    writer.save()
    print(f'Saved to {writer.path}')

 '''