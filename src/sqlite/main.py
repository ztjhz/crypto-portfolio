from sqlalchemy import create_engine
import pandas as pd


def initialise_engine(READ_FILE_NAME, RECORD_FILE_NAME):
    engine_1 = create_engine(f'sqlite:///{READ_FILE_NAME}', echo=False)
    engine_2 = create_engine(f'sqlite:///{RECORD_FILE_NAME}', echo=False)
    return engine_1, engine_2


def read_data(engine_1):

    portfolio_df = pd.read_sql_table("portfolio", engine_1, index_col="SYMBOL")
    portfolio_df.sort_index(inplace=True)

    tx_df = pd.read_sql_table("transactions", engine_1, index_col="TX_ID")

    withdrawal_df = pd.read_sql_table("withdrawals",
                                      engine_1,
                                      index_col="WITHDRAWAL_ID")

    deposit_df = pd.read_sql_table("deposits",
                                   engine_1,
                                   index_col="DEPOSIT_ID")

    record_df = pd.read_sql_table("records", engine_1, index_col="DATE")

    average_cost_df = pd.read_sql_table("average_costs",
                                        engine_1,
                                        index_col="SYMBOL")

    coin_id_df = pd.read_sql_table("coin_id", engine_1, index_col="SYMBOL")

    type_df = pd.read_sql_table("types", engine_1, index_col="TYPE_ID")

    return portfolio_df, tx_df, withdrawal_df, deposit_df, record_df, average_cost_df, coin_id_df, type_df


# save to database
def save_data(portfolio_df, record_df, deposit_df, withdrawal_df, tx_df,
              average_cost_df, type_df, coin_id_df, updateAveragePrice,
              getPriceDF, engine_1, engine_2, DATE):
    updateAveragePrice()

    engines = [engine_1, engine_2]

    price_df = getPriceDF('sgd')
    total = price_df['TOTAL'].sum()
    totalDeposited = deposit_df['AMOUNT'].sum()
    totalWithDrawn = withdrawal_df['AMOUNT'].sum()
    totalPL = totalWithDrawn + total - totalDeposited
    percentagePL = (totalPL / totalDeposited) * 100

    if DATE not in list(record_df.index.values):
        new_df = pd.DataFrame(
            {
                'TOTAL DEPOSITED': [totalDeposited],
                'TOTAL WITHDRAWN': [totalWithDrawn],
                'PORTFOLIO VALUE': [total],
                'TOTAL P/L': [totalPL],
                '% P/L': [percentagePL]
            },
            index=[DATE])
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
                portfolio_df.to_sql("portfolio",
                                    con=engine,
                                    if_exists="replace")
                tx_df.to_sql("transactions", con=engine, if_exists="replace")
                deposit_df.to_sql("deposits", con=engine, if_exists="replace")
                withdrawal_df.to_sql("withdrawals",
                                     con=engine,
                                     if_exists="replace")
                record_df.to_sql("records", con=engine, if_exists="replace")
                average_cost_df.to_sql("average_costs",
                                       con=engine,
                                       if_exists="replace")
                coin_id_df.to_sql("coin_id", con=engine, if_exists="replace")
                type_df.to_sql("types", con=engine, if_exists="replace")

                print(f"Saved at {engine.url}")
                success = True
        except IOError:
            print("IOError! Trying again...")

    success = False
