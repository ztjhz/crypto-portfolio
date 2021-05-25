from numpy.core.fromnumeric import transpose
from requests_html import HTMLSession
import pandas as pd
import datetime
import json
import requests
import time
import os
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

from sqlalchemy import create_engine
from dotenv import load_dotenv

def get_yahoo_finance_USD_SGD_rate():
    url = "https://sg.finance.yahoo.com/quote/USDSGD=X/"
    try:
        session = HTMLSession()
        response = session.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
    
    USDSGD = float(response.html.xpath("//span[@data-reactid='32']")[0].text)
    return(USDSGD)

def get_mas_USD_SGD_rate():
    api_link = "https://eservices.mas.gov.sg/api/action/datastore/search.json?resource_id=95932927-c8bc-4e7a-b484-68a66a24edfe&fields=usd_sgd,end_of_day&limit=1&sort=end_of_day%20desc"
    r = requests.get(api_link).json()
    while r["success"] != True:
        print("Failed to get USDSGD rate. Trying again...")
        r = requests.get(api_link).json()
    USDSGD = float(r["result"]["records"][0]["usd_sgd"])

    return USDSGD
    
def read_data():

    portfolio_df = pd.read_sql_table("portfolio", engine_1, index_col="SYMBOL")
    portfolio_df.sort_index(inplace=True)

    tx_df = pd.read_sql_table("transactions", engine_1, index_col="TX_ID")

    withdrawal_df = pd.read_sql_table("withdrawals", engine_1, index_col="WITHDRAWAL_ID")

    deposit_df = pd.read_sql_table("deposits", engine_1, index_col="DEPOSIT_ID")

    record_df = pd.read_sql_table("records", engine_1, index_col="DATE")

    average_cost_df = pd.read_sql_table("average_costs", engine_1, index_col="SYMBOL")

    coin_id_df = pd.read_sql_table("coin_id", engine_1, index_col="SYMBOL")

    type_df = pd.read_sql_table("types", engine_1, index_col = "TYPE_ID")

    return portfolio_df, tx_df, withdrawal_df, deposit_df, record_df, average_cost_df, coin_id_df, type_df

load_dotenv()
USERNAME = os.getenv("COIN_GECKO_USERNAME")
PASSWORD = os.getenv("COIN_GECKO_PASSWORD")
EXECUTABLE_PATH = os.getenv("CHROME_WEBDRIVER_EXECUTABLE_PATH")
DISPLAYPROFIT = False
CASHBACK = ["3% CASHBACK", "NETFLIX REBATE", "SPOTIFY REBATE", "CRYPTO PAY"]


# get exchange rate data
print("Getting USDSGD rate...")
USDSGD = get_yahoo_finance_USD_SGD_rate()
print("Obtained USDSGD rate!\n")


DATE = datetime.date.today().strftime('%d/%m/%Y')
record_date = datetime.date.today().strftime('%d-%m-%Y')
readFileName = "crypto.db"
recordFolderName = f"Record/{datetime.date.today().strftime('%Y-%m')}"
if not os.path.exists(recordFolderName):
    os.makedirs(recordFolderName)
    print(recordFolderName, 'created!')
recordFileName = f'{recordFolderName}/{record_date}.db'
averagePriceFileName = 'average_price.json'

engine_1 = create_engine(f'sqlite:///{readFileName}', echo=False)
engine_2 = create_engine(f'sqlite:///{recordFileName}', echo=False)

# depost_df, withdrawal_df, record_df are in sgd
# average_cost_df is in usd
success = False
while success == False:
    try:
        print(f"Reading {readFileName}...") 
        portfolio_df, tx_df, withdrawal_df, deposit_df, record_df, average_cost_df, coin_id_df, type_df = read_data()
        success = True
        print(f"{readFileName} has been read successfully!")
    except IOError:
        print(f"\n{readFileName} is open! Please close the file and try again.")
        input("Press enter to continue: ")

COINS = list(portfolio_df.index)
PLATFORM = list(portfolio_df.columns[:-1])
TYPE = list(type_df["TYPE"])
TYPE.sort()

pd.options.display.max_rows = len(COINS)
pd.options.display.max_columns = len(PLATFORM) + 1
pd.options.display.width = 200


# Get price in usd and sgd
def get_price():
    coinIDParam = ','.join(coin_id_df[coin_id_df['ACTIVE'] == True]['COIN ID'])
    currencyParam = ','.join(['usd', 'sgd'])
    payload = {'ids': coinIDParam, 'vs_currencies': currencyParam}
    r = requests.get('https://api.coingecko.com/api/v3/simple/price', params = payload)
    return r.json()
price_dict = get_price()

def get_price_all():
    coinIDParam = ','.join(coin_id_df['COIN ID'])
    currencyParam = ','.join(['usd', 'sgd'])
    payload = {'ids': coinIDParam, 'vs_currencies': currencyParam}
    r = requests.get('https://api.coingecko.com/api/v3/simple/price', params = payload)
    return r.json()

# deposit
def deposit(platform, amt:float, coin, quantity:float, remarks):
    global deposit_df
    global DATE
    db = pd.DataFrame({'DATE': DATE, 'AMOUNT': amt, 'COIN': coin, 'QUANTITY': quantity, 'REMARKS': remarks}, index=[deposit_df.index[-1] + 1])
    db.index.name = "DEPOSIT_ID"
    deposit_df = deposit_df.append(db)

    add_transactions(platform, coin, quantity, 'DEPOSIT', remarks)

# withdraw
def withdraw(platform, amt:float, coin, quantity:float, remarks):
    global withdrawal_df
    global DATE
    db = pd.DataFrame({'DATE': DATE, 'AMOUNT': amt, 'COIN': coin, 'QUANTITY': quantity, 'REMARKS': remarks}, index=[withdrawal_df.index[-1] + 1])
    db.index.name = "WITHDRAWAL_ID"
    withdrawal_df = withdrawal_df.append(db)

    add_transactions(platform, coin, -abs(quantity), 'WITHDRAW', remarks)

def add_transactions(platform, coin, quantity:float, Type, remarks):
    global tx_df
    global DATE
    global portfolio_df
    db = pd.DataFrame({'DATE': DATE, 'PLATFORM': platform, 'COIN': coin, 'QUANTITY': quantity, 'TYPE':Type, 'REMARKS': remarks, "CALCULATED": False}, index=[tx_df.index[-1] + 1])
    db.index.name = "TX_ID"
    tx_df = tx_df.append(db)

    portfolio_df.loc[coin, [platform, 'TOTAL']] += quantity
    print()
    printHeading("Transaction completed:")
    print(f'Date: {DATE}\nPlatform: {platform}\nCoin: {coin}\nQuantity: {quantity}\nType: {Type}\nRemarks: {remarks}\n')
    return f"{DATE}, {platform}, {coin}, {quantity}, {Type}, {remarks}"

def displayCoinsAvailable():
    print('Coins available: ')
    for i in range(len(COINS)):
        print(f'{i}: {COINS[i]}')

def displayPlatformsAvailable():
    print('Platform available: ')
    for i in range(len(PLATFORM)):
        print(f'{i}: {PLATFORM[i]}')

def displayTypesAvailable():
    print('Type of Transactions Available:')
    for i in range(len(TYPE)):
        print(f'{i}: {TYPE[i]}')

def displayOptions():
    print('\n')
    print('0. Display Portfolio')
    print('1. Deposit')
    print('2. Withdrawal')
    print('3. Transfer coins between platforms')
    print('4. Convert from one coin into another')
    print('5. Display Database')
    print('6. Add Transaction')
    print('7. Add / Remove Coin')
    print('8. Add / Remove Platform')
    print('9. Save and exit')
    print('10. Save File')
    print('11. Exit')
    print('x. Update CoinGecko')
    print('c. Add cashback')
    print('u. Upload app transaction file')
    print('g. Display Graph')

def sortPortfolioColumns(df):
    col = df.pop('TOTAL')
    df = df[sorted(df.columns)]
    df.insert(len(df.columns), 'TOTAL', col)
    return df

def getPriceDF(currency):
    price_df = pd.DataFrame()
    for i in range(len(COINS)):
        coinID = coin_id_df.loc[COINS[i], 'COIN ID']
        if coinID in price_dict:
            price = price_dict[coinID][currency]
        else:
            price = 0
        price_df = price_df.append(portfolio_df.loc[COINS[i]].map(lambda x: x * price))
    
    price_df = sortPortfolioColumns(price_df)

    return price_df

def addTransactionFee(remarks):
    displayCoinsAvailable()
    coin = COINS[int(input('Enter choice: '))]
    quantity = -abs(float(input("Enter quantity: ")))
    Type = 'TRANSACTION FEE'
    displayPlatformsAvailable()
    platform = PLATFORM[int(input("Enter where the tx fees were deducted from: "))]
    remarks = '(Transaction Fees) ' + remarks
    add_transactions(platform, coin, quantity, Type, remarks)

def display_graph():
    dates = pd.Series(x for x in record_df.index)
    tick_interval = int(len(record_df.index) / 26)

    matplotlib.style.use('ggplot')

    fg, ax = plt.subplots(figsize=(12,7))
    ax.plot(dates, record_df["TOTAL P/L"] / 1.33, label="1")
    #ax.plot(dates, record_df["PORTFOLIO VALUE"], label="2", linestyle="dashed")
    
    ax.set_xlabel("Date")
    ax.set_ylabel("P/L (USD)")
    ax.set_title("P/L Over Time")

    plt.xticks(dates[::tick_interval])
    plt.tight_layout()
    fg.autofmt_xdate()
    plt.show()

# save to database
def save_data():
    global portfolio_df
    global record_df
    updateAveragePrice()

    engines = [engine_1, engine_2]
    
    price_df = getPriceDF('sgd')
    total = price_df['TOTAL'].sum()
    totalDeposited = deposit_df['AMOUNT'].sum()
    totalWithDrawn = withdrawal_df['AMOUNT'].sum()
    totalPL = totalWithDrawn + total - totalDeposited
    percentagePL = (totalPL / totalDeposited) * 100

    if DATE not in list(record_df.index.values):
        new_df = pd.DataFrame({'TOTAL DEPOSITED': [totalDeposited], 'TOTAL WITHDRAWN': [totalWithDrawn], 'PORTFOLIO VALUE': [total], 'TOTAL P/L': [totalPL], '% P/L': [percentagePL]}, index=[DATE])
        new_df.index.name = 'DATE'
        record_df = record_df.append(new_df)
    else:
        record_df.loc[DATE, 'TOTAL DEPOSITED'] = totalDeposited
        record_df.loc[DATE, 'TOTAL WITHDRAWN'] = totalWithDrawn
        record_df.loc[DATE, 'PORTFOLIO VALUE'] = total
        record_df.loc[DATE, 'TOTAL P/L'] = totalPL
        record_df.loc[DATE, '% P/L'] = percentagePL
    
    success = False

    while success == False:
        try:
            for engine in engines:
                portfolio_df.to_sql("portfolio", con=engine, if_exists="replace")
                tx_df.to_sql("transactions", con=engine, if_exists="replace")
                deposit_df.to_sql("deposits", con=engine, if_exists="replace")
                withdrawal_df.to_sql("withdrawals", con=engine, if_exists="replace")
                record_df.to_sql("records", con=engine, if_exists="replace")
                average_cost_df.to_sql("average_costs", con=engine, if_exists="replace")
                coin_id_df.to_sql("coin_id", con=engine, if_exists="replace")
                type_df.to_sql("types", con=engine, if_exists="replace")

                print(f"Saved at {engine.url}")
                success = True
        except IOError:
            print("IOError! Trying again...")
    
    success = False


def updateCoinGecko():
    opts = Options()
    opts.headless = False

    username = USERNAME
    password = PASSWORD
    executable_path = EXECUTABLE_PATH
    portfolio_url = 'https://www.coingecko.com/en/portfolio'

    browser = Chrome(options = opts, executable_path=executable_path)
    browser.implicitly_wait(10)

    browser.get(portfolio_url)

    # accept cookies
    browser.find_element_by_xpath("//button[@data-action='click->cookie-note#accept']").click()

    # Log in
    browser.find_element_by_id('user_email').send_keys(f'{username}')
    browser.find_element_by_id('user_password').send_keys(f'{password}')
    browser.find_element_by_xpath("//input[@value = 'Log in']").submit()

    updated = False

    while not updated:
        if browser.current_url != portfolio_url:
            browser.get(portfolio_url)
        # Get links to the different coins
        elements = browser.find_elements_by_xpath("//td[@class = 'text-right col-gecko no-wrap']/a")

        all_links = {}
        quantity_list = []
        unstarList = []
        for element in elements:
            link = element.get_attribute('href')
            oldQuantity, symbol = element.find_elements_by_xpath(".//div[@class='text-black']")[1].text.split(' ')
            if symbol not in portfolio_df.index:
                unstarList.append(symbol)
                continue
            newQuantity = str(portfolio_df.loc[symbol, 'TOTAL'])
            price = average_cost_df.loc[symbol, 'AVERAGE COST']
            all_links[link] = [symbol, newQuantity, price]
            if oldQuantity != newQuantity:
                quantity_list.append(symbol)

        for symbol in unstarList:
            unstarButton = browser.find_element_by_xpath(f"//td[@class='pl-1 pr-0']/i[@data-coin-symbol='{symbol.lower()}']")
            unstarButton.click()
            confirmationButton = browser.find_element_by_xpath("//button[@id='unfavourite-coin-confirm-button']")
            confirmationButton.click()
            while len(browser.find_elements_by_xpath(f"//td[@class='pl-1 pr-0']/i[@data-coin-symbol='{symbol.lower()}']")) != 0:
                pass
            print(f'{symbol} has been removed!')

        for link, data in all_links.items():
            # go to coin portfolio page
            while browser.current_url != link:
                browser.get(link)

            coin_symbol = data[0]
            quantity = data[1]
            price = data[2]

            update_price = False
            update_quantity = False

            try:
                # click on edit button
                edit_button = browser.find_element_by_xpath("//td/a[@class='text-primary']")
                edit_button.click()
                transaction_type = 'edit'

            except NoSuchElementException:
                # add new transaction
                new_transaction_button = browser.find_element_by_xpath("//div/a[@data-action='click->portfolio-coin-transactions-new#updateCoinIdValue']")
                new_transaction_button.click()
                transaction_type = 'new'

            current_quantity = browser.find_element_by_xpath("//td[@class='text-right']/span[@class='text-green']").text.lstrip("+")
            # enter new value into quantity
            quantity_field = browser.find_element_by_xpath(f"//input[@id='portfolio-coin-transactions-{transaction_type}_portfolio_coin_transaction_quantity']")
            if current_quantity != quantity:
                quantity_field.clear()
                quantity_field.send_keys(quantity)
                update_quantity = True
            price_element = browser.find_element_by_id(f"portfolio-coin-transactions-{transaction_type}_portfolio_coin_transaction_price")
            WebDriverWait(browser,10).until(lambda x: price_element.get_attribute('value') != '')
            current_price = float(price_element.get_attribute('value'))
            if current_price != price:
                browser.execute_script(f"document.getElementById('portfolio-coin-transactions-{transaction_type}_portfolio_coin_transaction_price').value={price}")
                update_price = True

            if update_price == True or update_quantity == True:
                quantity_field.send_keys(Keys.ENTER)
            if update_price == True and update_quantity == True:
                print(f'{quantity} {coin_symbol} (${price}) has been updated on CoinGecko!')
            elif update_price == True:
                print(f'{coin_symbol} (${price}) has been updated on CoinGecko!')
            elif update_quantity == True:
                print(f'{quantity} {coin_symbol} has been updated on CoinGecko!')
            
        updated = True
    
    browser.quit()

def getPortfolioChange(percentagePL, currentPL):
    currentValue = percentagePL
    days = [1, 7, 30, 60, 90, 120, 180, 270, 365]
    dates = {}

    for day in days: 
        dates[str(day) + 'd'] = (datetime.date.today() - datetime.timedelta(days = day)).strftime('%d/%m/%Y')

    df = pd.DataFrame(index=[str(day) + 'd' for day in days], columns=['%', 'USD', 'SGD'])

    for day, date in dates.items():
        if date not in record_df.index:
            df.loc[day, '%'] = 'NA'
            df.loc[day, 'SGD'] = 'NA'
            df.loc[day, 'USD'] = 'NA'
        else:

            PLValue = record_df.loc[date, 'TOTAL P/L']
            PLchange = currentPL - PLValue
            df.loc[day, 'SGD'] = '{:.2f}'.format(PLchange)
            df.loc[day, 'USD'] = '{:.2f}'.format(PLchange / USDSGD)

            portfolioValue = record_df.loc[date, '% P/L']
            change = currentValue - portfolioValue
            
            df.loc[day, '%'] = '{:.2f}'.format(change)
            
    return df

def displayPortfolioChange(change_df):
    heading = "Portfolio change over time:"
    print()
    printHeading(heading)
    print(change_df)


def getHistoricalPrice(coinID, date, currency='usd'):
    #coingecko format: dd-mm-yyyy
    query_date = date[:2] + '-' + date[3:5] + '-' + date[6:]
    r = requests.get('https://api.coingecko.com/api/v3/coins/{}/history?date={}&localization=false'.format(coinID, query_date))
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
            r = requests.get('https://api.coingecko.com/api/v3/coins/{}/history?date={}&localization=false'.format(coinID, query_date))
    return price

# calculate average purchasing price from entire transaction history
def calculateAveragePrice(coin):
    global tx_df
    global average_cost_df
    NEU_TX = ['CRYPTO EARN', 'AIRDROP', 'STAKING REWARD', 'CASHBACK', 'TRANSACTION FEE', 'ARBITRAGE', 'YIELD FARMING', 'CASHBACK REVERSAL', 'CRYPTO.COM ADJUSTMENT', 'TRADING', 'REBATE']
    IGN_TX = ['TRANSFER']
    NORMAL_TX = ['CONVERT', 'DEPOSIT', 'WITHDRAW']
    total_quantity = 0
    total_cost = 0
    average_cost = 0
    if coin in average_cost_df.index:
        total_cost = average_cost_df.loc[coin, 'TOTAL COST']
        total_quantity = average_cost_df.loc[coin, 'TOTAL QUANTITY']
        average_cost = average_cost_df.loc[coin, 'AVERAGE COST']
    coin_tx_df = tx_df[(tx_df['COIN'] == coin) & (tx_df['CALCULATED'] == False)]

    for i, row in coin_tx_df.iterrows():
        type = row['TYPE']
        quantity = row['QUANTITY']
        date = row['DATE']
        if date == DATE:
            continue
        price = getHistoricalPrice(coin_id_df.loc[coin, 'COIN ID'], date)
        print(coin, date, type, quantity, price, end="")

        if type in IGN_TX:
            print(" - ignored")
        elif type in NEU_TX:
            print(" - neutral")
            total_quantity += quantity
        elif type in NORMAL_TX:
            # Deposit / Withrawal / Conversion
            print(" - added")

            # When you sell, the price you sell at does not matter for the determination of your average cost. 
            # You reduce the number of shares by the number of shares in the transaction
            # You reduce the total cost by the (average price)*(number of shares in the transaction). 
            # This means that selling does not change the average price, just the number of shares.
            if quantity < 0: # selling a transaction 
                average_cost = total_cost / total_quantity
                total_cost += quantity * average_cost # = subtraction

            # When you buy more shares, 
            # The total cost goes up by the total you paid in the transaction (=(# shares in the transaction) * (transaction price))
            # The number of shares increases by the amount in the transaction. 
            # You get the average cost by dividing the total cost by the number of shares.
            else:
                total_cost += quantity * price
            total_quantity += quantity

            # Your profit on selling is based on comparing the selling price to the average cost. 
            # This would be the “cost of goods sold” in inventory accounting. 
            # (If you want more details on this subject, you could look for primers on inventory accounting on the internet.)
        else:
            print(f"{type} not in transaction_type.txt")
            exit()
        tx_df.loc[i, "CALCULATED"] = True
        
    if total_quantity != 0 and total_cost != 0:
        average_cost = total_cost / total_quantity

    return total_cost, total_quantity, average_cost


# Update average_price.json with average price of all coins and all transaction history 
def updateAveragePrice():
    global average_cost_df
    for coin in coin_id_df.index:
        total_cost, total_quantity, average_cost = calculateAveragePrice(coin)
        if coin not in average_cost_df.index:
            average_cost_df = average_cost_df.append(pd.Series({'TOTAL COST': total_cost,'TOTAL QUANTITY': total_quantity,'AVERAGE COST': average_cost, 'ACTIVE': True}, name = coin))
            average_cost_df.sort_values(by = ['ACTIVE', 'SYMBOL'], ascending = [False, True], inplace=True)
        else:
            average_cost_df.loc[coin, 'TOTAL COST'] = total_cost
            average_cost_df.loc[coin, 'TOTAL QUANTITY'] = total_quantity
            average_cost_df.loc[coin, 'AVERAGE COST'] = average_cost

def getProfitPerCoin(all=False):
    profit_per_coin = {}
    price_dict_all = get_price_all()

    coin_list = []
    if all == True:
        coin_list = list(average_cost_df.index)
    else:
        coin_list = list(average_cost_df[average_cost_df['ACTIVE'] == True].index)

    for coin in coin_list:
        total_quantity = average_cost_df.loc[coin, 'TOTAL QUANTITY']
        if total_quantity == 0:
            profit_per_coin[coin] = {"PROFIT": "NA", "%": "NA", "Active": coin_id_df.loc[coin, 'ACTIVE']}
            continue
        #cost = total_quantity * average_price_dict[coinID]['Average Price']
        cost = average_cost_df.loc[coin, 'AVERAGE COST'] * total_quantity
        current_value = total_quantity * price_dict_all[coin_id_df.loc[coin, 'COIN ID']]['usd']
        profit = current_value - cost
        if cost <= 0:
            percentage_profit = "NA"
        else:
            percentage_profit = profit / cost * 100
        profit_per_coin[coin] = {"PROFIT": profit, "%": percentage_profit, "Active": coin_id_df.loc[coin, 'ACTIVE']}
    
    return profit_per_coin

def displayProfitPerCoin(inactive=False):
    profit_per_coin = getProfitPerCoin(all=True)
    for v in profit_per_coin.values():
        if v['PROFIT'] != "NA":
            v['PROFIT'] = "{:.2f}".format(v['PROFIT'])
        if v['%'] != 'NA':
            v['%'] = float("{:.2f}".format(v['%']))
    df = pd.DataFrame(profit_per_coin).transpose()
    # sort by %
    display_df = pd.DataFrame(df[(df['%'] != 'NA') & (df['Active'] == True)].sort_values(by='%', ascending=False))
    # sort by profit for those with NA %
    display_df = display_df.append(df[ (df['%'] == 'NA') & (df['PROFIT'] != 'NA') & (df['Active'] == True)].sort_values(by='PROFIT', ascending=False))
    
    display_df.drop("Active", axis=1, inplace=True)
    #df.sort_values(by='%', inplace=True, ascending=False)
    #df.rename_axis("COIN", inplace=True)
    pd.options.display.max_rows = len(profit_per_coin)
    print(display_df)

    if inactive:
        print()
        printHeading("Inactive coins:")
        print(df[(df['Active'] == False) & (df['%'] != 'NA')].sort_values(by='PROFIT',ascending=True).drop("Active", axis=1))

# upload transaction excel file downloaded from Crypto.com App
def uploadCryptoTransaction():
    transaction_folder = 'app_transaction'
    files_in_dir = os.listdir(transaction_folder)
    required_file_name_prefix = 'crypto_transactions_record_{}'.format(datetime.date.today().strftime("%Y%m%d"))
    file_path = ""
    ignore_list = ['crypto_withdrawal', 'crypto_deposit', 'crypto_earn_program_created', 'crypto_earn_program_withdrawn']
    ignored_transactions = []
    processed_transactions = []

    for i in files_in_dir:
        if required_file_name_prefix in i:
            file_path = os.path.join(transaction_folder, i)
    if file_path == "":
        print(f'\nTransaction file for {DATE} does not exist!')
        time.sleep(1)
        return
    t_df = pd.read_csv(file_path)
    t_df.sort_index(ascending=False, inplace=True)
    
    border_length = 50
    
    for index, row in t_df.iterrows():
        transaction_type = row['Transaction Kind']
        coin = row['Currency']
        quantity = abs(float(row['Amount']))
        raw_quantity = float(row['Amount'])
        processed = True
        remarks = ""
        print("-"*border_length)
        print(f"{transaction_type}: {raw_quantity} {coin}")
        
        # Crypto Earn
        if transaction_type == 'crypto_earn_interest_paid':
            crypto_earn_types = ["FLEXIBLE", "1 MONTH", '3 MONTH']
            print("CRYPTO EARN: ", quantity, coin)
            for i in range(len(crypto_earn_types)):
                print(f"{i}. {crypto_earn_types[i]}")
            remarks = crypto_earn_types[int(input("Select the type: "))]
            add_transactions("APP", coin, quantity, 'CRYPTO EARN', remarks)

        # MCO Card Staking Rewards
        elif transaction_type == 'mco_stake_reward':
            remarks = "CRYPTO.COM APP STAKING REWARD"
            add_transactions('APP', coin, quantity, "STAKING REWARD", remarks)

        # Card Cashback + Rebate
        elif transaction_type == 'referral_card_cashback' or transaction_type == 'reimbursement':
            remarks = row['Transaction Description']
            add_transactions("APP", coin, quantity, 'CASHBACK', remarks)

        # Cash Back Reversal
        elif transaction_type == 'reimbursement_reverted' or transaction_type == 'card_cashback_reverted':
            remarks = row['Transaction Description']
            add_transactions("APP", coin, -quantity, 'CASHBACK REVERSAL', remarks)

        # Crypto.com Adjustment (Credit)
        elif transaction_type == 'admin_wallet_credited':
            remarks = row['Transaction Description']
            add_transactions("APP", coin, quantity, 'CRYPTO.COM ADJUSTMENT', remarks)

        # Supercharger Deposit / Withdrawal
        elif transaction_type == 'supercharger_deposit':
            remarks = f"Transfer {quantity} {coin} from APP to SUPERCHARGER"
            add_transactions("APP", coin, -quantity, "TRANSFER", remarks)
            add_transactions("SUPERCHARGER", coin, quantity, "TRANSFER", remarks)
        elif transaction_type == 'supercharger_withdrawal':
            remarks = f"Transfer {quantity} {coin} from SUPERCHARGER to APP"
            add_transactions("APP", coin, quantity, "TRANSFER", remarks)
            add_transactions("SUPERCHARGER", coin, -quantity, "TRANSFER", remarks)
        
        # Transfer from App to Exchange or Exchange to App
        elif transaction_type == 'exchange_to_crypto_transfer':
            remarks = f"Transfer {quantity} {coin} from EXCHANGE to APP"
            add_transactions("APP", coin, quantity, "TRANSFER", remarks)
            add_transactions("EXCHANGE", coin, -quantity, "TRANSFER", remarks)
        elif transaction_type == 'crypto_to_exchange_transfer':
            remarks = f"Transfer {quantity} {coin} from APP to EXCHANGE"
            add_transactions("APP", coin, -quantity, "TRANSFER", remarks)
            add_transactions("EXCHANGE", coin, quantity, "TRANSFER", remarks)
        
        # Convert dust crypto to CRO on App
        elif transaction_type == 'dust_conversion_credited':
            remarks = "CONVERT DUST CRYPTO TO CRO ON APP"
            add_transactions("APP", coin, quantity, "CONVERT", remarks)
        elif transaction_type == 'dust_conversion_debited':
            remarks = f"CONVERT DUST {coin} TO CRO ON APP"
            add_transactions("APP", coin, -quantity, "CONVERT", remarks)

        # Convert crypto in App
        elif transaction_type == 'crypto_exchange':
            fromCoin = coin
            fromQuantity = -quantity
            toCoin = row['To Currency']
            toQuantity = row['To Amount']
            remarks = f"Convert from {abs(fromQuantity)} {fromCoin} to {toQuantity} {toCoin} on APP"
            add_transactions("APP", fromCoin, fromQuantity, "CONVERT", remarks)
            add_transactions("APP", toCoin, toQuantity, "CONVERT", remarks)

        # Buy Crypto via Xfers
        elif transaction_type == 'xfers_purchase':
            amount = quantity
            coin = row['To Currency']
            coin_quantity = abs(float(row['To Amount']))
            remarks = "XFERS"
            deposit("APP", amount, coin, coin_quantity, remarks)
            print(deposit_df.tail())

        # Buy Crypto using Debit (No Cross Border Fees)
        elif transaction_type == 'crypto_purchase':
            remarks = "DEBIT CARD"
            amount = abs(float(row['Native Amount']))
            deposit("APP", amount, coin, quantity, remarks)

        # Sell Crypto to top up MCO card
        elif transaction_type == 'card_top_up':
            remarks = "CARD"
            amount = abs(float(row['Native Amount']))
            withdraw("APP", amount, coin, quantity, remarks)

        


        # Ignore transactions
        elif transaction_type in ignore_list:
            print("Transaction ignored")
            ignored_transactions.append(f"{transaction_type}: {quantity} {coin}")
            processed = False
        
        # transaction type not in the excel file
        else:
            processed = False
            print(f"{transaction_type} not in program!")
            exit()
        
        if processed:
            processed_transactions.append(f"({transaction_type}: {raw_quantity} {coin}) {remarks}")
        print("-"*border_length)
        print()
    if len(processed_transactions) > 0:
        print("\nProcessed Transactions:")
        for tx in processed_transactions:
            print(tx)
    if len(ignored_transactions) > 0:
        print("\nIgnored Transactions:")
        for tx in ignored_transactions:
            print(tx)


def printHeading(heading):
    print("-"*len(heading))
    print(heading)
    print("-"*len(heading))

def main():
    global portfolio_df
    global record_df
    global price_dict
    global coin_id_df
    global average_cost_df
    global type_df
    global COINS
    global PLATFORM
    global TYPE

    Exit = False
    while Exit != True:

        displayOptions()

        choice = input("Enter your choice: ")

        # Display Portfolio
        if choice == '0':
            perCoin = False
            if DISPLAYPROFIT:
                x = input("Display Profit Per Coin? [y/n] ")
                if x == 'y':
                    perCoin = True

            currencies = ['usd', 'sgd']
            totalDict = {}
            for currency in currencies:
                price_df = getPriceDF(currency)
                total = price_df['TOTAL'].sum()
                totalDict[currency] = total
                pd.set_option('precision', 2)
                totalPerPlatform = {}
                for platform in price_df.columns:
                    totalPerPlatform[platform] = price_df[platform].sum()
                temp_df = pd.DataFrame(totalPerPlatform, index = ['TOTAL'])
                price_df = price_df.append(temp_df)
                pd.options.display.max_rows = len(COINS) + 1

                portfolio_total = price_df.loc['TOTAL', 'TOTAL']
                price_df.insert(len(price_df.columns), '%', ["{:.2f}".format((x/portfolio_total)* 100) for x in price_df['TOTAL'].values])
                pd.options.display.max_columns += 1

                if perCoin:
                    profit_per_coin = getProfitPerCoin()
                    price_df.insert(len(price_df.columns), 'PROFIT', ["{:.2f}".format(x['PROFIT']) if x['PROFIT'] != 'NA' else "NA" for x in profit_per_coin.values()] + ["{:.2f}".format(sum([x['PROFIT'] if x['PROFIT'] != 'NA' else 0 for x in profit_per_coin.values()]))])
                    pd.options.display.max_columns += 1
                

                print(price_df)

                pd.options.display.max_rows = len(COINS)
                pd.reset_option('precision')
                heading = 'Total in {}: ${:.2f}'.format(currency.upper(), total)
                print("-" * len(heading))
                print(heading)
                print("-" * len(heading))
                print()
            
            totalDeposited = deposit_df['AMOUNT'].sum()
            totalWithDrawn = withdrawal_df['AMOUNT'].sum()
            currentPL = totalWithDrawn + totalDict['sgd'] - totalDeposited
            percentagePL = (currentPL / totalDeposited) * 100
            SGDheading = "Portfolio summary in SGD:"
            USDheading = 'Portfolio summary in USD:'

            print('{:<40s}'.format("-" * len(SGDheading)), end='')
            print('{:<40s}'.format("-" * len(USDheading)))

            print('{:<40s}'.format(SGDheading), end='')
            print('{:<40s}'.format(USDheading))

            print('{:<40s}'.format("-" * len(SGDheading)), end='')
            print('{:<40s}'.format("-" * len(USDheading)))

            print('{:<40s}'.format('Total deposited: ${:.2f}'.format(totalDeposited)), end='')
            print('{:<40s}'.format('Total deposited: ${:.2f}'.format(totalDeposited / USDSGD)))

            print('{:<40s}'.format('Total withdrawn: ${:.2f}'.format(totalWithDrawn)), end = '')
            print('{:<40s}'.format('Total withdrawn: ${:.2f}'.format(totalWithDrawn / USDSGD)))

            print('{:<40s}'.format('Portfolio value: ${:.2f}'.format(totalDict['sgd'])), end = '')
            print('{:<40s}'.format('Portfolio value: ${:.2f}'.format(totalDict['usd'])))
            
            print('{:<40s}'.format('Total P/L: ${:.2f} ({:.2f}%)'.format(totalWithDrawn + totalDict['sgd'] - totalDeposited, percentagePL)), end = '')
            print('{:<40s}'.format('Total P/L: ${:.2f} ({:.2f}%)'.format((totalWithDrawn / USDSGD) + totalDict['usd'] - (totalDeposited / USDSGD), percentagePL)))

            change_df = getPortfolioChange(percentagePL, currentPL)
            displayPortfolioChange(change_df)

            if perCoin:
                printHeading('Profit Per Coin:')
                inactiveCoin = False
                x = input("Display Inactive Coins? [y/n] ")
                if x == 'y':
                    inactiveCoin = True
                print()
                displayProfitPerCoin(inactiveCoin)
        elif choice == 'z':
            updateAveragePrice()
        # Deposit
        elif choice == '1':
            displayCoinsAvailable()
            coin = COINS[int(input('Enter choice: '))]
            
            displayPlatformsAvailable()
            platform = PLATFORM[int(input('Enter choice: '))]

            amt = float(input('Enter amount paid in SGD: '))
            quantity = float(input('Enter the number of coins received: '))
            remarks = input('Enter your remarks: ')
            deposit(platform, amt, coin, quantity, remarks)
        
        # Withdrawal
        elif choice == '2':
            displayCoinsAvailable()
            coin = COINS[int(input('Enter choice: '))]
            
            displayPlatformsAvailable()
            platform = PLATFORM[int(input('Enter choice: '))]

            amt = float(input('Enter amount received in SGD: '))
            quantity = float(input('Enter the number of coins sold: '))
            remarks = input('Enter your remarks: ')
            withdraw(platform, amt, coin, quantity, remarks)

        # Transfer coin from one platform to another
        elif choice == '3':
            displayCoinsAvailable()
            coin = COINS[int(input('Enter choice: '))]
            quantity = abs(float(input("Enter quantity: ")))

            displayPlatformsAvailable()
            platformFrom = PLATFORM[int(input(f'Transfer from: '))]

            displayPlatformsAvailable()
            platformTo = PLATFORM[int(input(f'Transfer to: '))]

            Type = 'TRANSFER'
            remarks = f'Transfer {quantity} {coin} from {platformFrom} to {platformTo}'

            add_transactions(platformFrom, coin, -quantity, Type, remarks)
            add_transactions(platformTo, coin, quantity, Type, remarks)
            
            tx = input('Is there transaction fees? (y/n) ')
            if tx.lower() == "y":
                addTransactionFee(remarks)

        # Convert from one coin to another
        elif choice =='4':
            displayPlatformsAvailable()
            platform = PLATFORM[int(input('Enter choice: '))]

            displayCoinsAvailable()
            coinFrom = COINS[int(input('Convert from: '))]
            quantityFrom = abs(float(input('Enter quantity: ')))
            displayCoinsAvailable()
            coinTo = COINS[int(input('Convert to: '))]
            quantityTo = abs(float(input('Enter quantity: ')))

            Type = 'CONVERT'
            remarks = f'Convert {quantityFrom} {coinFrom} to {quantityTo} {coinTo} on {platform}'
            add_transactions(platform, coinFrom, -quantityFrom, Type, remarks)
            add_transactions(platform, coinTo, quantityTo, Type, remarks)

            tx = input('Is there transaction fees? (y/n) ')
            if tx.lower() == "y":
                addTransactionFee(remarks)

        # Display Database
        elif choice == '5':
            print('\nPortfolio:')
            print(portfolio_df)
            print('\nDeposit:')
            print(deposit_df)
            print('\nWithdrawal:')
            print(withdrawal_df)
            print('\nTransaction:')
            print(tx_df)

        # Add Transaction
        elif choice == '6':
            displayPlatformsAvailable()
            platform = PLATFORM[int(input("Enter choice: "))]

            displayCoinsAvailable()
            coin = COINS[int(input('Enter choice: '))]
            quantity = float(input("Enter quantity: "))
            
            displayTypesAvailable()
            print(f'{len(TYPE)}: Create new type of transaction')
            typeChoice = int(input("Enter choice: "))
            if typeChoice == len(TYPE):
                Type = input('Enter transaction type: ').upper()

                TYPE.append(Type)
                TYPE.sort()

                temp_df = pd.DataFrame({"TYPE": Type}, index=[type_df.index[-1] + 1])
                temp_df.index.name = "TYPE_ID"
                type_df = type_df.append(temp_df)

                type_df.to_sql("types", engine_1, if_exists="replace")
                type_df.to_sql("types", engine_2, if_exists="replace")

                print('Saved new transaction type!')

            else:
                Type = TYPE[typeChoice]
                
            remarks = input('Enter remarks: ')

            if Type == 'TRANSACTION FEE' or Type == 'CASHBACK REVERSAL':
                quantity = -abs(quantity)

            add_transactions(platform, coin, quantity, Type, remarks)

        # Add / Remove Coin
        elif choice == '7':
            choice2 = input('Add (a) / Remove (r): ')
            if choice2.lower() == 'a':
                coin = input('Enter symbol of the coin: ').upper()
                
                # add coin to portfolio dataframe
                temp_dict = {}
                for i in PLATFORM:
                    temp_dict[i] = [0]
                temp_dict['TOTAL'] = [0]
                df = pd.DataFrame(temp_dict, index= [coin])
                df.index.name = 'SYMBOL'
                portfolio_df = portfolio_df.append(df)
                portfolio_df.sort_index(inplace=True)

                # add coin to json file
                coinID = input('Enter coin id from CoinGecko: ')
                if coin not in coin_id_df.index:
                    coin_id_df = coin_id_df.append(pd.Series({"COIN ID": coinID, 'ACTIVE': True}, name=coin))
                    coin_id_df.sort_values(by = ['ACTIVE', "SYMBOL"], ascending=[False, True], inplace=True)
                    average_cost_df = average_cost_df.append(pd.Series({'TOTAL COST': 0,'TOTAL QUANTITY': 0,'AVERAGE COST': 0, 'ACTIVE': True}, name = coin))
                    average_cost_df.sort_values(by = ['ACTIVE', 'SYMBOL'], ascending = [False, True], inplace=True)
                else:
                    coin_id_df.loc[coin, "ACTIVE"] = True
                    average_cost_df.loc[coin, "ACTIVE"] = True
                print(f'\n{coin} has been added.\n')

            elif choice2.lower() == 'r':
                displayCoinsAvailable()
                coin = COINS[int(input('Enter choice: '))]

                # remove coin from portfolio dataframe
                portfolio_df.drop(coin, inplace = True)

                # remove coin from json file
                coin_id_df.loc[coin, "ACTIVE"] = False
                coin_id_df.sort_values(by = ['ACTIVE', "SYMBOL"], ascending=[False, True], inplace=True)
                average_cost_df.loc[coin, "ACTIVE"] = False
                average_cost_df.sort_values(by = ['ACTIVE', "SYMBOL"], ascending=[False, True], inplace=True)
                print(f'\n{coin} has been removed\n')

            COINS = list(portfolio_df.index)
            pd.options.display.max_rows = len(COINS)

            price_dict = get_price()

        # Add / Remove Platform
        elif choice == '8':
            choice2 = input('Add (a) / Remove (r): ')
            if choice2.lower() == 'a':
                platform = input('Enter platform to add: ').upper()
                portfolio_df.insert(len(PLATFORM), platform, float(0))

                print(f'{platform} has been added')

                # arrange columns alphabetically
                #portfolio_df = portfolio_df[sorted(portfolio_df.columns[:-1]) + ['TOTAL']]
                portfolio_df = sortPortfolioColumns(portfolio_df)

            elif choice2.lower() == 'r':
                displayPlatformsAvailable()
                platform = PLATFORM[int(input("Enter choice: "))]
                for coin in COINS:
                    quantity = portfolio_df.loc[coin, platform]
                    if quantity != 0:
                        portfolio_df.loc[coin, 'TOTAL'] -= quantity
                portfolio_df.drop(platform, axis=1, inplace=True)
                print(f'\n{platform} has been removed\n')
                
            
            PLATFORM = list(portfolio_df.columns[:-1])
            pd.options.display.max_columns = len(PLATFORM) + 1

        # Save and Exit
        elif choice == '9':
            save_data()
            Exit = True

        # Save
        elif choice == '10':
            save_data()

        # Exit
        elif choice == '11':
            Exit = True
        
        # Display Portfolio (Update CoinGecko)
        elif choice == 'x':
            updateCoinGecko()
            
        # add cashback
        elif choice == 'c':
            for i in range(len(CASHBACK)):
                print("{}. {}".format(i, CASHBACK[i]))
            remarks = CASHBACK[int(input("Enter choice: "))]

            platform = "APP"
            coin = "CRO"
            quantity = float(input("Enter quantity of CRO received: "))
            Type = "CASHBACK"

            add_transactions(platform, coin, quantity, Type, remarks)

        elif choice == 'u':
            uploadCryptoTransaction()
        
        elif choice == 'g':
            display_graph()

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

if __name__ == "__main__":
    main()
