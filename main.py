""" Libararies """
import pandas as pd
import os
""" -------------------------------------- API calls -------------------------------------- """
from src.api.main import *
""" -------------------------------------- Displays -------------------------------------- """
from src.display.main import *
""" -------------------------------------- CoinGecko -------------------------------------- """
from src.coingecko.main import *
""" -------------------------------------- Env -------------------------------------- """
from src.env.main import *
""" -------------------------------------- Dataframe -------------------------------------- """
from src.dataframe.main import *


def main():
    data = Data(READ_FILE_NAME, RECORD_FILE_NAME, DATE, printHeading,
                getHistoricalPrice)
    USDSGD, price_dict, price_dict_all = api_call(data.getCoinIDParam())
    data.setUSDSGD(USDSGD)
    data.setPriceDict(price_dict)

    COINS = data.getCoin()
    PLATFORM = data.getPlatform()
    TYPE = data.getType()

    if not os.path.exists(RECORD_FOLDER_NAME):
        os.makedirs(RECORD_FOLDER_NAME)
        print(RECORD_FOLDER_NAME, 'created!')

    Exit = False
    while Exit != True:

        displayOptions()

        choice = input("Enter your choice: ")

        # ------------- Display Portfolio ---------------
        if choice == '0':
            currencies = ['usd', 'sgd']
            total_dict = {}
            per_coin = False

            for currency in currencies:
                price_df = data.getPriceDF(currency, price_dict)
                total = price_df['TOTAL'].sum()

                addTotalPerPlatformPriceDF(price_df, total_dict, currency,
                                           total, len(COINS))
                if DISPLAY_PROFIT:
                    per_coin = addProfitPerCoinPriceDF(data, price_dict_all,
                                                       price_df, per_coin)

                displayPortfolioDF(price_df, len(COINS), currency, total)

            displayPortfolioSummary(data, total_dict, USDSGD)
            if per_coin:
                displayProfitPerCoin(
                    data.getProfitPerCoin, True if
                    input("Display Inactive Coins? [y/n] ") == 'y' else False)

        elif choice == 'z':
            data.updateAveragePrice()

        # ------------- Deposit -------------
        elif choice == '1':
            displayCoinsAvailable(COINS)
            coin = COINS[int(input('Enter choice: '))]

            displayPlatformsAvailable(PLATFORM)
            platform = PLATFORM[int(input('Enter choice: '))]

            amt = float(input('Enter amount paid in SGD: '))
            quantity = float(input('Enter the number of coins received: '))
            remarks = input('Enter your remarks: ')
            data.deposit(platform, amt, coin, quantity, remarks)

        # ------------- Withdrawal -------------
        elif choice == '2':
            displayCoinsAvailable(data.getCoin())
            coin = COINS[int(input('Enter choice: '))]

            displayPlatformsAvailable(PLATFORM)
            platform = PLATFORM[int(input('Enter choice: '))]

            amt = float(input('Enter amount received in SGD: '))
            quantity = float(input('Enter the number of coins sold: '))
            remarks = input('Enter your remarks: ')
            data.withdraw(platform, amt, coin, quantity, remarks)

        # ------------- Transfer coin from one platform to another -------------
        elif choice == '3':
            displayCoinsAvailable(COINS)
            coin = COINS[int(input('Enter choice: '))]
            quantity = abs(float(input("Enter quantity: ")))

            displayPlatformsAvailable(PLATFORM)
            platformFrom = PLATFORM[int(input(f'Transfer from: '))]

            displayPlatformsAvailable(PLATFORM)
            platformTo = PLATFORM[int(input(f'Transfer to: '))]

            _type = 'TRANSFER'
            remarks = f'Transfer {quantity} {coin} from {platformFrom} to {platformTo}'

            data.add_transactions(platformFrom, coin, -quantity, _type,
                                  remarks)
            data.add_transactions(platformTo, coin, quantity, _type, remarks)

            tx = input('Is there transaction fees? (y/n) ')
            if tx.lower() == "y":
                data.addTransactionFee(remarks)

        # ------------- Convert from one coin to another -------------
        elif choice == '4':
            displayPlatformsAvailable(PLATFORM)
            platform = PLATFORM[int(input('Enter choice: '))]

            displayCoinsAvailable(COINS)
            coinFrom = COINS[int(input('Convert from: '))]
            quantityFrom = abs(float(input('Enter quantity: ')))
            displayCoinsAvailable(COINS)
            coinTo = COINS[int(input('Convert to: '))]
            quantityTo = abs(float(input('Enter quantity: ')))

            _type = 'CONVERT'
            remarks = f'Convert {quantityFrom} {coinFrom} to {quantityTo} {coinTo} on {platform}'
            data.add_transactions(platform, coinFrom, -quantityFrom, _type,
                                  remarks)
            data.add_transactions(platform, coinTo, quantityTo, _type, remarks)

            tx = input('Is there transaction fees? (y/n) ')
            if tx.lower() == "y":
                data.addTransactionFee(remarks)

        # ------------- Display Database -------------
        elif choice == '5':
            data.printDF()

        # ------------- Add Transaction -------------
        elif choice == '6':
            displayPlatformsAvailable(PLATFORM)
            platform = PLATFORM[int(input("Enter choice: "))]

            displayCoinsAvailable(COINS)
            coin = COINS[int(input('Enter choice: '))]
            quantity = float(input("Enter quantity: "))

            displayTypesAvailable(TYPE)
            print(f'{len(TYPE)}: Create new type of transaction')

            type_choice = int(input("Enter choice: "))
            if type_choice == len(TYPE):
                _type = input('Enter transaction type: ').upper()

                data.insertTransactionType(_type)
                TYPE = data.getType()
                print('Added new transaction type!')

            else:
                _type = TYPE[type_choice]

            remarks = input('Enter remarks: ')

            if _type == 'TRANSACTION FEE' or _type == 'CASHBACK REVERSAL':
                quantity = -abs(quantity)

            data.add_transactions(platform, coin, quantity, _type, remarks)

        # ------------- Add / Remove Coin -------------
        elif choice == '7':
            choice2 = input('Add (a) / Remove (r): ')
            if choice2.lower() == 'a':
                data.addCoin()
            elif choice2.lower() == 'r':
                displayCoinsAvailable(COINS)
                coin = COINS[int(input('Enter choice: '))]

                data.removeCoin(coin)
                print(f'\n{coin} has been removed\n')

            COINS = data.getCoin()
            pd.options.display.max_rows = len(COINS)

            price_dict = get_price(data.getCoinIDParam())

        # ------------- Add / Remove Platform -------------
        elif choice == '8':
            choice2 = input('Add (a) / Remove (r): ')
            if choice2.lower() == 'a':
                platform = input('Enter platform to add: ').upper()
                data.insertPlatform(platform)

            elif choice2.lower() == 'r':
                displayPlatformsAvailable(PLATFORM)
                platform = PLATFORM[int(input("Enter choice: "))]
                data.removePlatform(platform)
                print(f'\n{platform} has been removed\n')

        # ------------- Save and Exit -------------
        elif choice == '9':
            data.save_data()
            Exit = True

        # ------------- Save -------------
        elif choice == '10':
            data.save_data()

        # ------------- Exit -------------
        elif choice == '11':
            Exit = True

        # ------------- Update CoinGecko -------------
        elif choice == 'x':
            symbols, symbol_total_df, symbol_cost_df = data.getCoinGeckoVar()
            updateCoinGecko(symbols, symbol_total_df, symbol_cost_df)

        # ------------- add cashback -------------
        elif choice == 'c':
            for i in range(len(CASHBACK)):
                print("{}. {}".format(i, CASHBACK[i]))
            remarks = CASHBACK[int(input("Enter choice: "))]

            platform = "APP"
            coin = "CRO"
            quantity = float(input("Enter quantity of CRO received: "))
            _type = "CASHBACK"

            data.add_transactions(platform, coin, quantity, _type, remarks)

        # ------------- process transaction csv file -------------
        elif choice == 'u':
            data.uploadCryptoTransaction()

        # ------------- display matplotlib graph -------------
        elif choice == 'g':
            record_index, record_total_pl = data.getDisplayGraphVar()
            display_graph(record_index, record_total_pl)

        # ------------- display web graph -------------
        elif choice == 'gg':
            record_index, record_total_pl, record_total_deposited_withdrawn, record_portfolio_value = data.getDisplayGraphWebVar(
            )
            display_graph_web(record_index, record_total_pl,
                              record_total_deposited_withdrawn,
                              record_portfolio_value)


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


def addTotalPerPlatformPriceDF(price_df, total_dict, currency, total,
                               coin_count):
    """ Add the total amount per platform to the last row of price_df """
    total_dict[currency] = total
    pd.set_option('precision', 2)
    totalPerPlatform = {}
    for platform in price_df.columns:
        totalPerPlatform[platform] = price_df[platform].sum()
    temp_df = pd.DataFrame(totalPerPlatform, index=['TOTAL'])
    price_df = price_df.append(temp_df)
    pd.options.display.max_rows = coin_count + 1

    portfolio_total = price_df.loc['TOTAL', 'TOTAL']
    price_df.insert(len(price_df.columns), '%', [
        "{:.2f}".format((x / portfolio_total) * 100)
        for x in price_df['TOTAL'].values
    ])
    pd.options.display.max_columns += 1


if __name__ == "__main__":
    main()
