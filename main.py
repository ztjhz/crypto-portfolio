""" Libararies """
import pandas as pd
import datetime
import time
import os
from pprint import pprint
""" -------------------------------------- API calls -------------------------------------- """
from src.api.main import *
""" -------------------------------------- Displays -------------------------------------- """
from src.display.main import *
""" -------------------------------------- CoinGecko -------------------------------------- """
from src.coingecko.main import *
""" -------------------------------------- Env -------------------------------------- """
from src.env.main import *
""" -------------------------------------- Sqlite -------------------------------------- """
# from src.sqlite.main import *
""" -------------------------------------- Dataframe -------------------------------------- """
from src.dataframe.main import *

# engine_1, engine_2 = initialise_engine(readFileName, recordFileName)

# depost_df, withdrawal_df, record_df are in sgd
# average_cost_df is in usd
# success = False
# while success == False:
#     try:
#         print(f"Reading {readFileName}...")

#         portfolio_df, tx_df, withdrawal_df, deposit_df, record_df, average_cost_df, coin_id_df, type_df = read_data(
#             engine_1)
#         success = True
#         print(f"{readFileName} has been read successfully!")
#     except IOError:
#         print(
#             f"\n{readFileName} is open! Please close the file and try again.")
#         input("Press enter to continue: ")

# COINS = list(portfolio_df.index)
# PLATFORM = list(portfolio_df.columns[:-1])
# TYPE = list(type_df["TYPE"])
# TYPE.sort()

# pd.options.display.max_rows = len(COINS)
# pd.options.display.max_columns = len(PLATFORM) + 1
# pd.options.display.width = 200

# # deposit
# def deposit(platform, amt: float, coin, quantity: float, remarks):
#     global deposit_df
#     global DATE
#     db = pd.DataFrame(
#         {
#             'DATE': DATE,
#             'AMOUNT': amt,
#             'COIN': coin,
#             'QUANTITY': quantity,
#             'REMARKS': remarks
#         },
#         index=[deposit_df.index[-1] + 1])
#     db.index.name = "DEPOSIT_ID"
#     deposit_df = deposit_df.append(db)

#     add_transactions(platform, coin, quantity, 'DEPOSIT', remarks)

# # withdraw
# def withdraw(platform, amt: float, coin, quantity: float, remarks):
#     global withdrawal_df
#     global DATE
#     db = pd.DataFrame(
#         {
#             'DATE': DATE,
#             'AMOUNT': amt,
#             'COIN': coin,
#             'QUANTITY': quantity,
#             'REMARKS': remarks
#         },
#         index=[withdrawal_df.index[-1] + 1])
#     db.index.name = "WITHDRAWAL_ID"
#     withdrawal_df = withdrawal_df.append(db)

#     add_transactions(platform, coin, -abs(quantity), 'WITHDRAW', remarks,
#                      tx_df, portfolio_df, DATE, printHeading)

# def add_transactions(platform, coin, quantity: float, Type, remarks):
#     global tx_df
#     global DATE
#     global portfolio_df
#     db = pd.DataFrame(
#         {
#             'DATE': DATE,
#             'PLATFORM': platform,
#             'COIN': coin,
#             'QUANTITY': quantity,
#             'TYPE': Type,
#             'REMARKS': remarks,
#             "CALCULATED": False
#         },
#         index=[tx_df.index[-1] + 1])
#     db.index.name = "TX_ID"
#     tx_df = tx_df.append(db)

#     portfolio_df.loc[coin, [platform, 'TOTAL']] += quantity
#     print()
#     printHeading("Transaction completed:")
#     print(
#         f'Date: {DATE}\nPlatform: {platform}\nCoin: {coin}\nQuantity: {quantity}\nType: {Type}\nRemarks: {remarks}\n'
#     )
#     return f"{DATE}, {platform}, {coin}, {quantity}, {Type}, {remarks}"

# def sortPortfolioColumns(df):
#     col = df.pop('TOTAL')
#     df = df[sorted(df.columns)]
#     df.insert(len(df.columns), 'TOTAL', col)
#     return df

# def getPriceDF(currency):
#     price_df = pd.DataFrame()
#     for i in range(len(COINS)):
#         coinID = coin_id_df.loc[COINS[i], 'COIN ID']
#         if coinID in price_dict:
#             price = price_dict[coinID][currency]
#         else:
#             price = 0
#             if coinID == 'us dollar':
#                 if currency == 'sgd':
#                     price = USDSGD
#                 elif currency == 'usd':
#                     price = 1
#         price_df = price_df.append(
#             portfolio_df.loc[COINS[i]].map(lambda x: x * price))

#     price_df = sortPortfolioColumns(price_df)

#     return price_df

# def addTransactionFee(remarks):
#     displayCoinsAvailable(COINS)
#     coin = COINS[int(input('Enter choice: '))]
#     quantity = -abs(float(input("Enter quantity: ")))
#     Type = 'TRANSACTION FEE'
#     displayPlatformsAvailable(PLATFORM)
#     platform = PLATFORM[int(
#         input("Enter where the tx fees were deducted from: "))]
#     remarks = '(Transaction Fees) ' + remarks
#     add_transactions(platform, coin, quantity, Type, remarks)

# def getPortfolioChange(percentagePL, currentPL):
#     currentValue = percentagePL
#     days = [1, 7, 30, 60, 90, 120, 180, 270, 365]
#     dates = {}

#     for day in days:
#         dates[str(day) +
#               'd'] = (datetime.date.today() -
#                       datetime.timedelta(days=day)).strftime('%d/%m/%Y')

#     df = pd.DataFrame(index=[str(day) + 'd' for day in days],
#                       columns=['%', 'USD', 'SGD'])

#     for day, date in dates.items():
#         if date not in record_df.index:
#             df.loc[day, '%'] = 'NA'
#             df.loc[day, 'SGD'] = 'NA'
#             df.loc[day, 'USD'] = 'NA'
#         else:

#             PLValue = record_df.loc[date, 'TOTAL P/L']
#             PLchange = currentPL - PLValue
#             df.loc[day, 'SGD'] = '{:.2f}'.format(PLchange)
#             df.loc[day, 'USD'] = '{:.2f}'.format(PLchange / USDSGD)

#             portfolioValue = record_df.loc[date, '% P/L']
#             change = currentValue - portfolioValue

#             df.loc[day, '%'] = '{:.2f}'.format(change)

#     return df

# # calculate average purchasing price from entire transaction history
# def calculateAveragePrice(coin):
#     global tx_df
#     global average_cost_df
#     NEU_TX = [
#         'CRYPTO EARN', 'AIRDROP', 'STAKING REWARD', 'CASHBACK',
#         'TRANSACTION FEE', 'ARBITRAGE', 'YIELD FARMING', 'CASHBACK REVERSAL',
#         'CRYPTO.COM ADJUSTMENT', 'TRADING', 'REBATE'
#     ]
#     IGN_TX = ['TRANSFER']
#     NORMAL_TX = ['CONVERT', 'DEPOSIT', 'WITHDRAW']
#     total_quantity = 0
#     total_cost = 0
#     average_cost = 0
#     if coin in average_cost_df.index:
#         total_cost = average_cost_df.loc[coin, 'TOTAL COST']
#         total_quantity = average_cost_df.loc[coin, 'TOTAL QUANTITY']
#         average_cost = average_cost_df.loc[coin, 'AVERAGE COST']
#     coin_tx_df = tx_df[(tx_df['COIN'] == coin)
#                        & (tx_df['CALCULATED'] == False)]
#     hist_prices = {}
#     for i, row in coin_tx_df.iterrows():
#         type = row['TYPE']
#         quantity = row['QUANTITY']
#         date = row['DATE']
#         if date == DATE:
#             continue
#         if coin not in hist_prices:
#             hist_prices[coin] = getHistoricalPrice(
#                 coin_id_df.loc[coin, 'COIN ID'], date)
#         price = hist_prices[coin]
#         print(coin, date, type, quantity, price, end="")

#         if type in IGN_TX:
#             print(" - ignored")
#         elif type in NEU_TX:
#             print(" - neutral")
#             total_quantity += quantity
#         elif type in NORMAL_TX:
#             # Deposit / Withrawal / Conversion
#             print(" - added")

#             # When you sell, the price you sell at does not matter for the determination of your average cost.
#             # You reduce the number of shares by the number of shares in the transaction
#             # You reduce the total cost by the (average price)*(number of shares in the transaction).
#             # This means that selling does not change the average price, just the number of shares.
#             if quantity < 0:  # selling a transaction
#                 average_cost = total_cost / total_quantity
#                 total_cost += quantity * average_cost  # = subtraction

#             # When you buy more shares,
#             # The total cost goes up by the total you paid in the transaction (=(# shares in the transaction) * (transaction price))
#             # The number of shares increases by the amount in the transaction.
#             # You get the average cost by dividing the total cost by the number of shares.
#             else:
#                 total_cost += quantity * price
#             total_quantity += quantity

#             # Your profit on selling is based on comparing the selling price to the average cost.
#             # This would be the “cost of goods sold” in inventory accounting.
#             # (If you want more details on this subject, you could look for primers on inventory accounting on the internet.)
#         else:
#             print(f"{type} not in transaction_type.txt")
#             exit()
#         tx_df.loc[i, "CALCULATED"] = True

#     if total_quantity != 0 and total_cost != 0:
#         average_cost = total_cost / total_quantity

#     return total_cost, total_quantity, average_cost

# # Update average_price.json with average price of all coins and all transaction history
# def updateAveragePrice():
#     global average_cost_df
#     for coin in coin_id_df.index:
#         total_cost, total_quantity, average_cost = calculateAveragePrice(coin)
#         if coin not in average_cost_df.index:
#             average_cost_df = average_cost_df.append(
#                 pd.Series(
#                     {
#                         'TOTAL COST': total_cost,
#                         'TOTAL QUANTITY': total_quantity,
#                         'AVERAGE COST': average_cost,
#                         'ACTIVE': True
#                     },
#                     name=coin))
#             average_cost_df.sort_values(by=['ACTIVE', 'SYMBOL'],
#                                         ascending=[False, True],
#                                         inplace=True)
#         else:
#             average_cost_df.loc[coin, 'TOTAL COST'] = total_cost
#             average_cost_df.loc[coin, 'TOTAL QUANTITY'] = total_quantity
#             average_cost_df.loc[coin, 'AVERAGE COST'] = average_cost

# def getProfitPerCoin(all=False):
#     profit_per_coin = {}
#     price_dict_all = get_price_all(coin_id_df)

#     coin_list = []
#     if all == True:
#         coin_list = list(average_cost_df.index)
#     else:
#         coin_list = list(
#             average_cost_df[average_cost_df['ACTIVE'] == True].index)

#     for coin in coin_list:
#         total_quantity = average_cost_df.loc[coin, 'TOTAL QUANTITY']
#         if total_quantity == 0:
#             profit_per_coin[coin] = {
#                 "PROFIT": "NA",
#                 "%": "NA",
#                 "Active": coin_id_df.loc[coin, 'ACTIVE']
#             }
#             continue
#         #cost = total_quantity * average_price_dict[coinID]['Average Price']
#         cost = average_cost_df.loc[coin, 'AVERAGE COST'] * total_quantity
#         current_value = total_quantity * price_dict_all[coin_id_df.loc[
#             coin, 'COIN ID']]['usd']
#         profit = current_value - cost
#         if cost <= 0:
#             percentage_profit = "NA"
#         else:
#             percentage_profit = profit / cost * 100
#         profit_per_coin[coin] = {
#             "PROFIT": profit,
#             "%": percentage_profit,
#             "Active": coin_id_df.loc[coin, 'ACTIVE']
#         }

#     return profit_per_coin

# # upload transaction excel file downloaded from Crypto.com App
# def uploadCryptoTransaction():
#     transaction_folder = 'app_transaction'
#     files_in_dir = os.listdir(transaction_folder)
#     required_file_name_prefix = 'crypto_transactions_record_{}'.format(
#         datetime.date.today().strftime("%Y%m%d"))
#     file_path = ""
#     ignore_list = [
#         'crypto_withdrawal', 'crypto_deposit', 'crypto_earn_program_created',
#         'crypto_earn_program_withdrawn'
#     ]
#     ignored_transactions = []
#     processed_transactions = []

#     for i in files_in_dir:
#         if required_file_name_prefix in i:
#             file_path = os.path.join(transaction_folder, i)
#     if file_path == "":
#         print(f'\nTransaction file for {DATE} does not exist!')
#         time.sleep(1)
#         return
#     t_df = pd.read_csv(file_path)
#     t_df.sort_index(ascending=False, inplace=True)

#     border_length = 50

#     for index, row in t_df.iterrows():
#         transaction_type = row['Transaction Kind']
#         coin = row['Currency']
#         quantity = abs(float(row['Amount']))
#         raw_quantity = float(row['Amount'])
#         processed = True
#         remarks = ""
#         print("-" * border_length)
#         print(f"{transaction_type}: {raw_quantity} {coin}")

#         # Crypto Earn
#         if transaction_type == 'crypto_earn_interest_paid':
#             crypto_earn_types = ["FLEXIBLE", "1 MONTH", '3 MONTH']
#             print("CRYPTO EARN: ", quantity, coin)
#             for i in range(len(crypto_earn_types)):
#                 print(f"{i}. {crypto_earn_types[i]}")
#             remarks = crypto_earn_types[int(input("Select the type: "))]
#             add_transactions("APP", coin, quantity, 'CRYPTO EARN', remarks)

#         # MCO Card Staking Rewards
#         elif transaction_type == 'mco_stake_reward':
#             remarks = "CRYPTO.COM APP STAKING REWARD"
#             add_transactions('APP', coin, quantity, "STAKING REWARD", remarks)

#         # Card Cashback + Rebate
#         elif transaction_type == 'referral_card_cashback' or transaction_type == 'reimbursement':
#             remarks = row['Transaction Description']
#             add_transactions("APP", coin, quantity, 'CASHBACK', remarks)

#         # Cash Back Reversal
#         elif transaction_type == 'reimbursement_reverted' or transaction_type == 'card_cashback_reverted':
#             remarks = row['Transaction Description']
#             add_transactions("APP", coin, -quantity, 'CASHBACK REVERSAL',
#                              remarks)

#         # Crypto.com Adjustment (Credit)
#         elif transaction_type == 'admin_wallet_credited':
#             remarks = row['Transaction Description']
#             add_transactions("APP", coin, quantity, 'CRYPTO.COM ADJUSTMENT',
#                              remarks)

#         # Supercharger Deposit / Withdrawal
#         elif transaction_type == 'supercharger_deposit':
#             remarks = f"Transfer {quantity} {coin} from APP to SUPERCHARGER"
#             add_transactions("APP", coin, -quantity, "TRANSFER", remarks)
#             add_transactions("SUPERCHARGER", coin, quantity, "TRANSFER",
#                              remarks)
#         elif transaction_type == 'supercharger_withdrawal':
#             remarks = f"Transfer {quantity} {coin} from SUPERCHARGER to APP"
#             add_transactions("APP", coin, quantity, "TRANSFER", remarks)
#             add_transactions("SUPERCHARGER", coin, -quantity, "TRANSFER",
#                              remarks)

#         # Transfer from App to Exchange or Exchange to App
#         elif transaction_type == 'exchange_to_crypto_transfer':
#             remarks = f"Transfer {quantity} {coin} from EXCHANGE to APP"
#             add_transactions("APP", coin, quantity, "TRANSFER", remarks)
#             add_transactions("EXCHANGE", coin, -quantity, "TRANSFER", remarks)
#         elif transaction_type == 'crypto_to_exchange_transfer':
#             remarks = f"Transfer {quantity} {coin} from APP to EXCHANGE"
#             add_transactions("APP", coin, -quantity, "TRANSFER", remarks)
#             add_transactions("EXCHANGE", coin, quantity, "TRANSFER", remarks)

#         # Convert dust crypto to CRO on App
#         elif transaction_type == 'dust_conversion_credited':
#             remarks = "CONVERT DUST CRYPTO TO CRO ON APP"
#             add_transactions("APP", coin, quantity, "CONVERT", remarks)
#         elif transaction_type == 'dust_conversion_debited':
#             remarks = f"CONVERT DUST {coin} TO CRO ON APP"
#             add_transactions("APP", coin, -quantity, "CONVERT", remarks)

#         # Convert crypto in App
#         elif transaction_type == 'crypto_exchange':
#             fromCoin = coin
#             fromQuantity = -quantity
#             toCoin = row['To Currency']
#             toQuantity = row['To Amount']
#             remarks = f"Convert from {abs(fromQuantity)} {fromCoin} to {toQuantity} {toCoin} on APP"
#             add_transactions("APP", fromCoin, fromQuantity, "CONVERT", remarks)
#             add_transactions("APP", toCoin, toQuantity, "CONVERT", remarks)

#         # Supercharger App reward
#         elif transaction_type == 'supercharger_reward_to_app_credited':
#             remarks = "CRYPTO.COM SUPERCHARGER APP REWARD"
#             if coin not in coin_id_df.index:
#                 addCoin(coin)
#             add_transactions("APP", coin, quantity, "STAKING REWARD", remarks)

#         # Buy Crypto via Xfers
#         elif transaction_type == 'xfers_purchase':
#             amount = quantity
#             coin = row['To Currency']
#             coin_quantity = abs(float(row['To Amount']))
#             remarks = "XFERS"
#             deposit("APP", amount, coin, coin_quantity, remarks)
#             print(deposit_df.tail())

#         # Buy Crypto using Debit (No Cross Border Fees)
#         elif transaction_type == 'crypto_purchase':
#             remarks = "DEBIT CARD"
#             amount = abs(float(row['Native Amount']))
#             deposit("APP", amount, coin, quantity, remarks)

#         # Sell Crypto to top up MCO card
#         elif transaction_type == 'card_top_up':
#             remarks = "CARD"
#             amount = abs(float(row['Native Amount']))
#             withdraw("APP", amount, coin, quantity, remarks)

#         # USD bank transfer to USDC
#         elif transaction_type == 'usdc_bank_deposit':
#             amount = abs(float(row['Native Amount']))
#             remarks = f"Deposit ${amount} USD (${amount * USDSGD} SGD) via USD bank transfer"
#             deposit("APP", amount * USDSGD, coin, quantity, remarks)

#         # Ignore transactions
#         elif transaction_type in ignore_list:
#             print("Transaction ignored")
#             ignored_transactions.append(
#                 f"{transaction_type}: {quantity} {coin}")
#             processed = False

#         # transaction type not in the excel file
#         else:
#             processed = False
#             print(f"{transaction_type} not in program!")
#             exit()

#         if processed:
#             processed_transactions.append(
#                 f"({transaction_type}: {raw_quantity} {coin}) {remarks}")
#         print("-" * border_length)
#         print()
#     if len(processed_transactions) > 0:
#         print("\nProcessed Transactions:")
#         for tx in processed_transactions:
#             print(tx)
#     if len(ignored_transactions) > 0:
#         print("\nIgnored Transactions:")
#         for tx in ignored_transactions:
#             print(tx)

# def addCoin(coin=None):
#     global portfolio_df, coin_id_df, average_cost_df

#     if not coin:
#         coin = input('Enter symbol of the coin: ').upper()
#     # add coin to portfolio dataframe
#     temp_dict = {}
#     for i in PLATFORM:
#         temp_dict[i] = [0]
#     temp_dict['TOTAL'] = [0]
#     df = pd.DataFrame(temp_dict, index=[coin])
#     df.index.name = 'SYMBOL'
#     portfolio_df = portfolio_df.append(df)
#     portfolio_df.sort_index(inplace=True)

#     coinID = input(f'Enter coin id of {coin} from CoinGecko: ')
#     if coin not in coin_id_df.index:
#         coin_id_df = coin_id_df.append(
#             pd.Series({
#                 "COIN ID": coinID,
#                 'ACTIVE': True
#             }, name=coin))
#         coin_id_df.sort_values(by=['ACTIVE', "SYMBOL"],
#                                ascending=[False, True],
#                                inplace=True)
#         average_cost_df = average_cost_df.append(
#             pd.Series(
#                 {
#                     'TOTAL COST': 0,
#                     'TOTAL QUANTITY': 0,
#                     'AVERAGE COST': 0,
#                     'ACTIVE': True
#                 },
#                 name=coin))
#         average_cost_df.sort_values(by=['ACTIVE', 'SYMBOL'],
#                                     ascending=[False, True],
#                                     inplace=True)
#     else:
#         coin_id_df.loc[coin, "ACTIVE"] = True
#         average_cost_df.loc[coin, "ACTIVE"] = True
#     print(f'\n{coin} has been added.\n')


def api_call(coin_id_param):
    print("Getting USDSGD rate...")
    USDSGD = get_yahoo_finance_USD_SGD_rate()
    print("Obtained USDSGD rate!\n")

    price_dict = get_price(coin_id_param)
    price_dict_all = get_price_all(coin_id_param)

    return USDSGD, price_dict, price_dict_all


def addProfitPerCoinPriceDF(data, price_dict_all, price_df, per_coin=False):
    """ Add the profit per coin to the last column of price_df """
    if input("Display Profit Per Coin? [y/n] ") == 'y':
        per_coin = True

    if per_coin:
        profit_per_coin = data.getProfitPerCoin(price_dict_all)
        price_df.insert(len(price_df.columns), 'PROFIT', [
            "{:.2f}".format(x['PROFIT']) if x['PROFIT'] != 'NA' else "NA"
            for x in profit_per_coin.values()
        ] + [
            "{:.2f}".format(
                sum([
                    x['PROFIT'] if x['PROFIT'] != 'NA' else 0
                    for x in profit_per_coin.values()
                ]))
        ])
        pd.options.display.max_columns += 1

    return per_coin


def addTotalPerPlatformPriceDF(price_df, total_dict, currency, total, data):
    """ Add the total amount per platform to the last row of price_df """
    total_dict[currency] = total
    pd.set_option('precision', 2)
    totalPerPlatform = {}
    for platform in price_df.columns:
        totalPerPlatform[platform] = price_df[platform].sum()
    temp_df = pd.DataFrame(totalPerPlatform, index=['TOTAL'])
    price_df = price_df.append(temp_df)
    pd.options.display.max_rows = data.getCoinCount() + 1

    portfolio_total = price_df.loc['TOTAL', 'TOTAL']
    price_df.insert(len(price_df.columns), '%', [
        "{:.2f}".format((x / portfolio_total) * 100)
        for x in price_df['TOTAL'].values
    ])
    pd.options.display.max_columns += 1

def main():
    USDSGD, price_dict, price_dict_all = api_call(data.getCoinIDParam())
    data = Data(READ_FILE_NAME, RECORD_FILE_NAME, DATE, USDSGD, printHeading)

    if not os.path.exists(RECORD_FOLDER_NAME):
        os.makedirs(RECORD_FOLDER_NAME)
        print(RECORD_FOLDER_NAME, 'created!')

    Exit = False
    while Exit != True:

        displayOptions()

        choice = input("Enter your choice: ")

        # Display Portfolio
        if choice == '0':
            currencies = ['usd', 'sgd']
            total_dict = {}
            per_coin = False

            for currency in currencies:
                price_df = data.getPriceDF(currency, price_dict)
                total = price_df['TOTAL'].sum()

                addTotalPerPlatformPriceDF(price_df, total_dict, currency,
                                           total, data)
                if DISPLAY_PROFIT:
                    per_coin = addProfitPerCoinPriceDF(data, price_dict_all, price_df, per_coin)

                print(price_df)

                pd.options.display.max_rows = len(COINS)
                pd.reset_option('precision')
                heading = 'Total in {}: ${:.2f}'.format(
                    currency.upper(), total)
                print("-" * len(heading))
                print(heading)
                print("-" * len(heading))
                print()

            displayPortfolioSummary(data, total_dict, USDSGD)
            if per_coin:
                displayProfitPerCoin(data.getProfitPerCoin, True if input("Display Inactive Coins? [y/n] ") == 'y' else False)

        elif choice == 'z':
            data.updateAveragePrice()
        # Deposit
        elif choice == '1':
            displayCoinsAvailable(COINS)
            coin = COINS[int(input('Enter choice: '))]

            displayPlatformsAvailable(PLATFORM)
            platform = PLATFORM[int(input('Enter choice: '))]

            amt = float(input('Enter amount paid in SGD: '))
            quantity = float(input('Enter the number of coins received: '))
            remarks = input('Enter your remarks: ')
            deposit(platform, amt, coin, quantity, remarks)

        # Withdrawal
        elif choice == '2':
            displayCoinsAvailable(COINS)
            coin = COINS[int(input('Enter choice: '))]

            displayPlatformsAvailable(PLATFORM)
            platform = PLATFORM[int(input('Enter choice: '))]

            amt = float(input('Enter amount received in SGD: '))
            quantity = float(input('Enter the number of coins sold: '))
            remarks = input('Enter your remarks: ')
            withdraw(platform, amt, coin, quantity, remarks)

        # Transfer coin from one platform to another
        elif choice == '3':
            displayCoinsAvailable(COINS)
            coin = COINS[int(input('Enter choice: '))]
            quantity = abs(float(input("Enter quantity: ")))

            displayPlatformsAvailable(PLATFORM)
            platformFrom = PLATFORM[int(input(f'Transfer from: '))]

            displayPlatformsAvailable(PLATFORM)
            platformTo = PLATFORM[int(input(f'Transfer to: '))]

            Type = 'TRANSFER'
            remarks = f'Transfer {quantity} {coin} from {platformFrom} to {platformTo}'

            add_transactions(platformFrom, coin, -quantity, Type, remarks)
            add_transactions(platformTo, coin, quantity, Type, remarks)

            tx = input('Is there transaction fees? (y/n) ')
            if tx.lower() == "y":
                addTransactionFee(remarks)

        # Convert from one coin to another
        elif choice == '4':
            displayPlatformsAvailable(PLATFORM)
            platform = PLATFORM[int(input('Enter choice: '))]

            displayCoinsAvailable(COINS)
            coinFrom = COINS[int(input('Convert from: '))]
            quantityFrom = abs(float(input('Enter quantity: ')))
            displayCoinsAvailable(COINS)
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
            displayPlatformsAvailable(PLATFORM)
            platform = PLATFORM[int(input("Enter choice: "))]

            displayCoinsAvailable(COINS)
            coin = COINS[int(input('Enter choice: '))]
            quantity = float(input("Enter quantity: "))

            displayTypesAvailable(TYPE)()
            print(f'{len(TYPE)}: Create new type of transaction')
            typeChoice = int(input("Enter choice: "))
            if typeChoice == len(TYPE):
                Type = input('Enter transaction type: ').upper()

                TYPE.append(Type)
                TYPE.sort()

                temp_df = pd.DataFrame({"TYPE": Type},
                                       index=[type_df.index[-1] + 1])
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
                addCoin()
                '''
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
                '''

            elif choice2.lower() == 'r':
                displayCoinsAvailable(COINS)
                coin = COINS[int(input('Enter choice: '))]

                # remove coin from portfolio dataframe
                portfolio_df.drop(coin, inplace=True)

                # remove coin from json file
                coin_id_df.loc[coin, "ACTIVE"] = False
                coin_id_df.sort_values(by=['ACTIVE', "SYMBOL"],
                                       ascending=[False, True],
                                       inplace=True)
                average_cost_df.loc[coin, "ACTIVE"] = False
                average_cost_df.sort_values(by=['ACTIVE', "SYMBOL"],
                                            ascending=[False, True],
                                            inplace=True)
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
                displayPlatformsAvailable(PLATFORM)
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
            save_data(portfolio_df, record_df, deposit_df, withdrawal_df,
                      tx_df, average_cost_df, type_df, coin_id_df,
                      updateAveragePrice, getPriceDF, engine_1, engine_2, DATE)
            Exit = True

        # Save
        elif choice == '10':
            save_data(portfolio_df, record_df, deposit_df, withdrawal_df,
                      tx_df, average_cost_df, type_df, coin_id_df,
                      updateAveragePrice, getPriceDF, engine_1, engine_2, DATE)

        # Exit
        elif choice == '11':
            Exit = True

        # Display Portfolio (Update CoinGecko)
        elif choice == 'x':
            updateCoinGecko(portfolio_df, average_cost_df)

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
            display_graph(record_df)

        elif choice == 'gg':
            display_graph_web(record_df)


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
