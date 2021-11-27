from sqlalchemy import create_engine
import pandas as pd
import os, datetime, time


class Data:
    def __init__(self, READ_FILE_NAME, RECORD_FILE_NAME, DATE, USDSGD,
                 printHeading):
        self.__printHeading = printHeading
        self.__initialise_engine(READ_FILE_NAME, RECORD_FILE_NAME)
        self.__initialise_const(DATE, USDSGD)
        self.__initialise_pandas_config()
        self.__read_data(READ_FILE_NAME)

    def __initialise_engine(self, READ_FILE_NAME, RECORD_FILE_NAME):
        self.__engine_1 = create_engine(f'sqlite:///{READ_FILE_NAME}',
                                        echo=False)
        self.__engine_2 = create_engine(f'sqlite:///{RECORD_FILE_NAME}',
                                        echo=False)

    def __initialise_pandas_config(self):
        pd.options.display.max_rows = len(self.__COINS)
        pd.options.display.max_columns = len(self.__PLATFORM) + 1
        pd.options.display.width = 200

    def __initialise_const(self, DATE, USDSGD):
        self.__COINS = list(self.__portfolio_df.index)
        self.__PLATFORM = list(self.__portfolio_df.columns[:-1])
        self.__TYPE = list(self.__type_df["TYPE"])
        self.__TYPE.sort()
        self.__DATE = DATE
        self.__USDSGD = USDSGD
        self.__NEU_TX = [
            'CRYPTO EARN', 'AIRDROP', 'STAKING REWARD', 'CASHBACK',
            'TRANSACTION FEE', 'ARBITRAGE', 'YIELD FARMING',
            'CASHBACK REVERSAL', 'CRYPTO.COM ADJUSTMENT', 'TRADING', 'REBATE'
        ]
        self.__IGN_TX = ['TRANSFER']
        self.__NORMAL_TX = ['CONVERT', 'DEPOSIT', 'WITHDRAW']

    def __read_data(self, READ_FILE_NAME):
        success = False
        while success == False:
            try:
                print(f"Reading {READ_FILE_NAME}...")

                self.__portfolio_df = pd.read_sql_table("portfolio",
                                                        self.__engine_1,
                                                        index_col="SYMBOL")
                self.__portfolio_df.sort_index(inplace=True)

                self.__tx_df = pd.read_sql_table("transactions",
                                                 self.__engine_1,
                                                 index_col="TX_ID")

                self.__withdrawal_df = pd.read_sql_table(
                    "withdrawals", self.__engine_1, index_col="WITHDRAWAL_ID")

                self.__deposit_df = pd.read_sql_table("deposits",
                                                      self.__engine_1,
                                                      index_col="DEPOSIT_ID")

                self.__record_df = pd.read_sql_table("records",
                                                     self.__engine_1,
                                                     index_col="DATE")

                self.__average_cost_df = pd.read_sql_table("average_costs",
                                                           self.__engine_1,
                                                           index_col="SYMBOL")

                self.__coin_id_df = pd.read_sql_table("coin_id",
                                                      self.__engine_1,
                                                      index_col="SYMBOL")

                self.__type_df = pd.read_sql_table("types",
                                                   self.__engine_1,
                                                   index_col="TYPE_ID")

                success = True
                print(f"{READ_FILE_NAME} has been read successfully!")
            except IOError:
                print(
                    f"\n{READ_FILE_NAME} is open! Please close the file and try again."
                )
                input("Press enter to continue: ")

    # save to database
    def save_data(self, updateAveragePrice, getPriceDF):
        updateAveragePrice()

        engines = [self.__engine_1, self.__engine_2]

        price_df = getPriceDF('sgd')
        total = price_df['TOTAL'].sum()
        totalDeposited = self.__deposit_df['AMOUNT'].sum()
        totalWithDrawn = self.__withdrawal_df['AMOUNT'].sum()
        totalPL = totalWithDrawn + total - totalDeposited
        percentagePL = (totalPL / totalDeposited) * 100

        if self.__DATE not in list(self.__record_df.index.values):
            new_df = pd.DataFrame(
                {
                    'TOTAL DEPOSITED': [totalDeposited],
                    'TOTAL WITHDRAWN': [totalWithDrawn],
                    'PORTFOLIO VALUE': [total],
                    'TOTAL P/L': [totalPL],
                    '% P/L': [percentagePL]
                },
                index=[self.__DATE])
            new_df.index.name = 'DATE'
            self.__record_df = self.__record_df.append(new_df)
        else:
            self.__record_df.loc[self.__DATE,
                                 'TOTAL DEPOSITED'] = totalDeposited
            self.__record_df.loc[self.__DATE,
                                 'TOTAL WITHDRAWN'] = totalWithDrawn
            self.__record_df.loc[self.__DATE, 'PORTFOLIO VALUE'] = total
            self.__record_df.loc[self.__DATE, 'TOTAL P/L'] = totalPL
            self.__record_df.loc[self.__DATE, '% P/L'] = percentagePL

        success = False

        while success == False:
            try:
                for engine in engines:
                    self.__portfolio_df.to_sql("portfolio",
                                               con=engine,
                                               if_exists="replace")
                    self.__tx_df.to_sql("transactions",
                                        con=engine,
                                        if_exists="replace")
                    self.__deposit_df.to_sql("deposits",
                                             con=engine,
                                             if_exists="replace")
                    self.__withdrawal_df.to_sql("withdrawals",
                                                con=engine,
                                                if_exists="replace")
                    self.__record_df.to_sql("records",
                                            con=engine,
                                            if_exists="replace")
                    self.__average_cost_df.to_sql("average_costs",
                                                  con=engine,
                                                  if_exists="replace")
                    self.__coin_id_df.to_sql("coin_id",
                                             con=engine,
                                             if_exists="replace")
                    self.__type_df.to_sql("types",
                                          con=engine,
                                          if_exists="replace")

                    print(f"Saved at {engine.url}")
                    success = True
            except IOError:
                print("IOError! Trying again...")

        success = False

    def __sortPortfolioColumns(self, df):
        col = df.pop('TOTAL')
        df = df[sorted(df.columns)]
        df.insert(len(df.columns), 'TOTAL', col)
        return df

    def add_transactions(self, platform, coin, quantity: float, Type, remarks):
        db = pd.DataFrame(
            {
                'DATE': self.__DATE,
                'PLATFORM': platform,
                'COIN': coin,
                'QUANTITY': quantity,
                'TYPE': Type,
                'REMARKS': remarks,
                "CALCULATED": False
            },
            index=[self.__tx_df.index[-1] + 1])
        db.index.name = "TX_ID"
        self.__tx_df = self.__tx_df.append(db)

        self.__portfolio_df.loc[coin, [platform, 'TOTAL']] += quantity
        print()
        self.__printHeading("Transaction completed:")
        print(
            f'Date: {self.__DATE}\nPlatform: {platform}\nCoin: {coin}\nQuantity: {quantity}\nType: {Type}\nRemarks: {remarks}\n'
        )
        return f"{self.__DATE}, {platform}, {coin}, {quantity}, {Type}, {remarks}"

    def addTransactionFee(self, remarks, displayCoinsAvailable,
                          displayPlatformsAvailable):
        displayCoinsAvailable(self.__COINS)
        coin = self.__COINS[int(input('Enter choice: '))]
        quantity = -abs(float(input("Enter quantity: ")))
        Type = 'TRANSACTION FEE'
        displayPlatformsAvailable(self.__PLATFORM)
        platform = self.__PLATFORM[int(
            input("Enter where the tx fees were deducted from: "))]
        remarks = '(Transaction Fees) ' + remarks
        self.add_transactions(platform, coin, quantity, Type, remarks)

    # calculate average purchasing price from entire transaction history
    def calculateAveragePrice(self, coin, getHistoricalPrice):
        total_quantity = 0
        total_cost = 0
        average_cost = 0
        if coin in self.__average_cost_df.index:
            total_cost = self.__average_cost_df.loc[coin, 'TOTAL COST']
            total_quantity = self.__average_cost_df.loc[coin, 'TOTAL QUANTITY']
            average_cost = self.__average_cost_df.loc[coin, 'AVERAGE COST']
        coin_tx_df = self.__tx_df[(self.__tx_df['COIN'] == coin)
                                  & (self.__tx_df['CALCULATED'] == False)]
        hist_prices = {}
        for i, row in coin_tx_df.iterrows():
            type = row['TYPE']
            quantity = row['QUANTITY']
            date = row['DATE']
            if date == self.__DATE:
                continue
            if coin not in hist_prices:
                hist_prices[coin] = getHistoricalPrice(
                    self.__coin_id_df.loc[coin, 'COIN ID'], date)
            price = hist_prices[coin]
            print(coin, date, type, quantity, price, end="")

            if type in self.__IGN_TX:
                print(" - ignored")
            elif type in self.__NEU_TX:
                print(" - neutral")
                total_quantity += quantity
            elif type in self.__NORMAL_TX:
                # Deposit / Withrawal / Conversion
                print(" - added")
                if quantity < 0:  # selling a transaction
                    """ 
                    When you sell, the price you sell at does not matter for the determination of your average cost.
                    You reduce the number of shares by the number of shares in the transaction
                    You reduce the total cost by the (average price)*(number of shares in the transaction).
                    This means that selling does not change the average price, just the number of shares.
                    """
                    average_cost = total_cost / total_quantity
                    total_cost += quantity * average_cost  # = subtraction
                else:
                    """ 
                    When you buy more shares,
                    The total cost goes up by the total you paid in the transaction (=(# shares in the transaction) * (transaction price))
                    The number of shares increases by the amount in the transaction.
                    You get the average cost by dividing the total cost by the number of shares.
                    """
                    total_cost += quantity * price
                total_quantity += quantity
                """ 
                Your profit on selling is based on comparing the selling price to the average cost.
                This would be the “cost of goods sold” in inventory accounting.
                (If you want more details on this subject, you could look for primers on inventory accounting on the internet.)
                """
            else:
                print(f"{type} not in transaction_type.txt")
                exit()
            self.__tx_df.loc[i, "CALCULATED"] = True

        if total_quantity != 0 and total_cost != 0:
            average_cost = total_cost / total_quantity

        return total_cost, total_quantity, average_cost

    # Update average_price.json with average price of all coins and all transaction history
    def updateAveragePrice(self):
        for coin in self.__coin_id_df.index:
            total_cost, total_quantity, average_cost = self.__calculateAveragePrice(
                coin)
            if coin not in self.__average_cost_df.index:
                self.__average_cost_df = self.__average_cost_df.append(
                    pd.Series(
                        {
                            'TOTAL COST': total_cost,
                            'TOTAL QUANTITY': total_quantity,
                            'AVERAGE COST': average_cost,
                            'ACTIVE': True
                        },
                        name=coin))
                self.__average_cost_df.sort_values(by=['ACTIVE', 'SYMBOL'],
                                                   ascending=[False, True],
                                                   inplace=True)
            else:
                self.__average_cost_df.loc[coin, 'TOTAL COST'] = total_cost
                self.__average_cost_df.loc[coin,
                                           'TOTAL QUANTITY'] = total_quantity
                self.__average_cost_df.loc[coin, 'AVERAGE COST'] = average_cost

    # upload transaction excel file downloaded from Crypto.com App
    def uploadCryptoTransaction(self):
        transaction_folder = 'app_transaction'
        files_in_dir = os.listdir(transaction_folder)
        required_file_name_prefix = 'crypto_transactions_record_{}'.format(
            datetime.date.today().strftime("%Y%m%d"))
        file_path = ""
        ignore_list = [
            'crypto_withdrawal', 'crypto_deposit',
            'crypto_earn_program_created', 'crypto_earn_program_withdrawn'
        ]
        ignored_transactions = []
        processed_transactions = []

        for i in files_in_dir:
            if required_file_name_prefix in i:
                file_path = os.path.join(transaction_folder, i)
        if file_path == "":
            print(f'\nTransaction file for {self.__DATE} does not exist!')
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
            print("-" * border_length)
            print(f"{transaction_type}: {raw_quantity} {coin}")

            #  ------------------------------ Crypto Earn -------------------------------------
            if transaction_type == 'crypto_earn_interest_paid':
                crypto_earn_types = ["FLEXIBLE", "1 MONTH", '3 MONTH']
                print("CRYPTO EARN: ", quantity, coin)
                for i in range(len(crypto_earn_types)):
                    print(f"{i}. {crypto_earn_types[i]}")
                remarks = crypto_earn_types[int(input("Select the type: "))]
                self.__add_transactions("APP", coin, quantity, 'CRYPTO EARN',
                                        remarks)

            # ------------------------------- MCO Card Staking Rewards ------------------------
            elif transaction_type == 'mco_stake_reward':
                remarks = "CRYPTO.COM APP STAKING REWARD"
                self.__add_transactions('APP', coin, quantity,
                                        "STAKING REWARD", remarks)

            # ------------------------------- Card Cashback + Rebate ----------------------------
            elif transaction_type == 'referral_card_cashback' or transaction_type == 'reimbursement':
                remarks = row['Transaction Description']
                self.__add_transactions("APP", coin, quantity, 'CASHBACK',
                                        remarks)

            # ------------------------------- Cash Back Reversal ------------------------------------
            elif transaction_type == 'reimbursement_reverted' or transaction_type == 'card_cashback_reverted':
                remarks = row['Transaction Description']
                self.__add_transactions("APP", coin, -quantity,
                                        'CASHBACK REVERSAL', remarks)

            # ---------------------------------- Crypto.com Adjustment (Credit) ----------------------------
            elif transaction_type == 'admin_wallet_credited':
                remarks = row['Transaction Description']
                self.__add_transactions("APP", coin, quantity,
                                        'CRYPTO.COM ADJUSTMENT', remarks)

            # ---------------------------------- Supercharger Deposit / Withdrawal ---------------------
            elif transaction_type == 'supercharger_deposit':
                remarks = f"Transfer {quantity} {coin} from APP to SUPERCHARGER"
                self.__add_transactions("APP", coin, -quantity, "TRANSFER",
                                        remarks)
                self.__add_transactions("SUPERCHARGER", coin, quantity,
                                        "TRANSFER", remarks)
            elif transaction_type == 'supercharger_withdrawal':
                remarks = f"Transfer {quantity} {coin} from SUPERCHARGER to APP"
                self.__add_transactions("APP", coin, quantity, "TRANSFER",
                                        remarks)
                self.__add_transactions("SUPERCHARGER", coin, -quantity,
                                        "TRANSFER", remarks)

            # ------------------------- Transfer from App to Exchange or Exchange to App --------------
            elif transaction_type == 'exchange_to_crypto_transfer':
                remarks = f"Transfer {quantity} {coin} from EXCHANGE to APP"
                self.__add_transactions("APP", coin, quantity, "TRANSFER",
                                        remarks)
                self.__add_transactions("EXCHANGE", coin, -quantity,
                                        "TRANSFER", remarks)
            elif transaction_type == 'crypto_to_exchange_transfer':
                remarks = f"Transfer {quantity} {coin} from APP to EXCHANGE"
                self.__add_transactions("APP", coin, -quantity, "TRANSFER",
                                        remarks)
                self.__add_transactions("EXCHANGE", coin, quantity, "TRANSFER",
                                        remarks)

            # ---------------------------------- Convert dust crypto to CRO on App ---------------------
            elif transaction_type == 'dust_conversion_credited':
                remarks = "CONVERT DUST CRYPTO TO CRO ON APP"
                self.__add_transactions("APP", coin, quantity, "CONVERT",
                                        remarks)
            elif transaction_type == 'dust_conversion_debited':
                remarks = f"CONVERT DUST {coin} TO CRO ON APP"
                self.__add_transactions("APP", coin, -quantity, "CONVERT",
                                        remarks)

            # ---------------------------------- Convert crypto in App ---------------------------------
            elif transaction_type == 'crypto_exchange':
                fromCoin = coin
                fromQuantity = -quantity
                toCoin = row['To Currency']
                toQuantity = row['To Amount']
                remarks = f"Convert from {abs(fromQuantity)} {fromCoin} to {toQuantity} {toCoin} on APP"
                self.__add_transactions("APP", fromCoin, fromQuantity,
                                        "CONVERT", remarks)
                self.__add_transactions("APP", toCoin, toQuantity, "CONVERT",
                                        remarks)

            # ---------------------------------- Supercharger App reward -------------------------------
            elif transaction_type == 'supercharger_reward_to_app_credited':
                remarks = "CRYPTO.COM SUPERCHARGER APP REWARD"
                if coin not in self.__coin_id_df.index:
                    self.addCoin(coin)
                self.__add_transactions("APP", coin, quantity,
                                        "STAKING REWARD", remarks)

            # ---------------------------------- Buy Crypto via Xfers -----------------------------
            elif transaction_type == 'xfers_purchase':
                amount = quantity
                coin = row['To Currency']
                coin_quantity = abs(float(row['To Amount']))
                remarks = "XFERS"
                self.__deposit("APP", amount, coin, coin_quantity, remarks)
                print(self.__deposit_df.tail())

            # ---------------------------------- Buy Crypto using Debit (No Cross Border Fees) ----------
            elif transaction_type == 'crypto_purchase':
                remarks = "DEBIT CARD"
                amount = abs(float(row['Native Amount']))
                self.__deposit("APP", amount, coin, quantity, remarks)

            # ---------------------------------- Sell Crypto to top up MCO card ---------------------
            elif transaction_type == 'card_top_up':
                remarks = "CARD"
                amount = abs(float(row['Native Amount']))
                self.__withdraw("APP", amount, coin, quantity, remarks)

            # ---------------------------------- USD bank transfer to USDC --------------------------
            elif transaction_type == 'usdc_bank_deposit':
                amount = abs(float(row['Native Amount']))
                remarks = f"Deposit ${amount} USD (${amount * self.__USDSGD} SGD) via USD bank transfer"
                self.__deposit("APP", amount * self.__USDSGD, coin, quantity,
                               remarks)

            # ---------------------------------- Ignore transactions --------------------------------
            elif transaction_type in ignore_list:
                print("Transaction ignored")
                ignored_transactions.append(
                    f"{transaction_type}: {quantity} {coin}")
                processed = False

            # ---------------------------------- transaction type not in the excel file ----------------
            else:
                processed = False
                print(f"{transaction_type} not in program!")
                exit()

            if processed:
                processed_transactions.append(
                    f"({transaction_type}: {raw_quantity} {coin}) {remarks}")
            print("-" * border_length)
            print()
        if len(processed_transactions) > 0:
            print("\nProcessed Transactions:")
            for tx in processed_transactions:
                print(tx)
        if len(ignored_transactions) > 0:
            print("\nIgnored Transactions:")
            for tx in ignored_transactions:
                print(tx)

    def addCoin(self, coin=None):
        if not coin:
            coin = input('Enter symbol of the coin: ').upper()

        # add coin to portfolio dataframe
        temp_dict = {}
        for i in self.__PLATFORM:
            temp_dict[i] = [0]
        temp_dict['TOTAL'] = [0]
        df = pd.DataFrame(temp_dict, index=[coin])
        df.index.name = 'SYMBOL'
        self.__portfolio_df = self.__portfolio_df.append(df)
        self.__portfolio_df.sort_index(inplace=True)

        coinID = input(f'Enter coin id of {coin} from CoinGecko: ')
        if coin not in self.__coin_id_df.index:
            self.__coin_id_df = self.__coin_id_df.append(
                pd.Series({
                    "COIN ID": coinID,
                    'ACTIVE': True
                }, name=coin))
            self.__coin_id_df.sort_values(by=['ACTIVE', "SYMBOL"],
                                          ascending=[False, True],
                                          inplace=True)
            self.__average_cost_df = self.__average_cost_df.append(
                pd.Series(
                    {
                        'TOTAL COST': 0,
                        'TOTAL QUANTITY': 0,
                        'AVERAGE COST': 0,
                        'ACTIVE': True
                    },
                    name=coin))
            self.__average_cost_df.sort_values(by=['ACTIVE', 'SYMBOL'],
                                               ascending=[False, True],
                                               inplace=True)
        else:
            self.__coin_id_df.loc[coin, "ACTIVE"] = True
            self.__average_cost_df.loc[coin, "ACTIVE"] = True
        print(f'\n{coin} has been added.\n')

    # deposit
    def deposit(self, platform, amt: float, coin, quantity: float, remarks):
        db = pd.DataFrame(
            {
                'DATE': self.__DATE,
                'AMOUNT': amt,
                'COIN': coin,
                'QUANTITY': quantity,
                'REMARKS': remarks
            },
            index=[self.__deposit_df.index[-1] + 1])
        db.index.name = "DEPOSIT_ID"
        self.__deposit_df = self.__deposit_df.append(db)

        self.__add_transactions(platform, coin, quantity, 'DEPOSIT', remarks)

    # withdraw
    def withdraw(self, platform, amt: float, coin, quantity: float, remarks):
        db = pd.DataFrame(
            {
                'DATE': self.__DATE,
                'AMOUNT': amt,
                'COIN': coin,
                'QUANTITY': quantity,
                'REMARKS': remarks
            },
            index=[self.__withdrawal_df.index[-1] + 1])
        db.index.name = "WITHDRAWAL_ID"
        self.__withdrawal_df = self.__withdrawal_df.append(db)

        self.add_transactions(platform, coin, -abs(quantity), 'WITHDRAW',
                              remarks)

    def getProfitPerCoin(self, price_dict_all, all=False):
        profit_per_coin = {}

        coin_list = []
        if all == True:
            coin_list = list(self.__average_cost_df.index)
        else:
            coin_list = list(self.__average_cost_df[
                self.__average_cost_df['ACTIVE'] == True].index)

        for coin in coin_list:
            total_quantity = self.__average_cost_df.loc[coin, 'TOTAL QUANTITY']
            if total_quantity == 0:
                profit_per_coin[coin] = {
                    "PROFIT": "NA",
                    "%": "NA",
                    "Active": self.__coin_id_df.loc[coin, 'ACTIVE']
                }
                continue
            #cost = total_quantity * average_price_dict[coinID]['Average Price']
            cost = self.__average_cost_df.loc[coin,
                                              'AVERAGE COST'] * total_quantity
            current_value = total_quantity * price_dict_all[
                self.__coin_id_df.loc[coin, 'COIN ID']]['usd']
            profit = current_value - cost
            if cost <= 0:
                percentage_profit = "NA"
            else:
                percentage_profit = profit / cost * 100
            profit_per_coin[coin] = {
                "PROFIT": profit,
                "%": percentage_profit,
                "Active": self.__coin_id_df.loc[coin, 'ACTIVE']
            }

        return profit_per_coin

    def getPortfolioChange(self, percentagePL, currentPL):
        currentValue = percentagePL
        days = [1, 7, 30, 60, 90, 120, 180, 270, 365]
        dates = {}

        for day in days:
            dates[str(day) +
                  'd'] = (datetime.date.today() -
                          datetime.timedelta(days=day)).strftime('%d/%m/%Y')

        df = pd.DataFrame(index=[str(day) + 'd' for day in days],
                          columns=['%', 'USD', 'SGD'])

        for day, date in dates.items():
            if date not in self._record_df.index:
                df.loc[day, '%'] = 'NA'
                df.loc[day, 'SGD'] = 'NA'
                df.loc[day, 'USD'] = 'NA'
            else:

                PLValue = self.__record_df.loc[date, 'TOTAL P/L']
                PLchange = currentPL - PLValue
                df.loc[day, 'SGD'] = '{:.2f}'.format(PLchange)
                df.loc[day, 'USD'] = '{:.2f}'.format(PLchange / self.__USDSGD)

                portfolioValue = self.__record_df.loc[date, '% P/L']
                change = currentValue - portfolioValue

                df.loc[day, '%'] = '{:.2f}'.format(change)

        return df

    def getPriceDF(self, currency, price_dict):
        price_df = pd.DataFrame()
        for i in range(len(self.__COINS)):
            coinID = self.__coin_id_df.loc[self.__COINS[i], 'COIN ID']
            if coinID in price_dict:
                price = price_dict[coinID][currency]
            else:
                price = 0
                if coinID == 'us dollar':
                    if currency == 'sgd':
                        price = self.__USDSGD
                    elif currency == 'usd':
                        price = 1
            price_df = price_df.append(self.__portfolio_df.loc[
                self.__COINS[i]].map(lambda x: x * price))

        price_df = self.__sortPortfolioColumns(price_df)

        return price_df

    def getDataFrames(self):
        return (self.__portfolio_df, self.__record_df, self.__price_dict,
                self.__coin_id_df, self.__average_cost_df, self.__type_df)

    def getTotalDeposit(self):
        """ Returns total deposit """
        return self.__deposit_df['AMOUNT'].sum()

    def getTotalWithdrawal(self):
        """ Returns total withdrawal """
        return self.__withdrawal_df['AMOUNT'].sum()

    def getCoinIDParam(self):
        """ Returns the coin ID parameters for CoinGecko API """
        return ','.join(
            self.__coin_id_df[self.__coin_id_df['ACTIVE'] == True]['COIN ID'])

    def getCoinCount(self):
        return self.__COINS