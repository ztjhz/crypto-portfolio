from sqlalchemy import create_engine
import pandas as pd

def initialise_engine(readFileName, recordFileName):
    engine_1 = create_engine(f'sqlite:///{readFileName}', echo=False)
    engine_2 = create_engine(f'sqlite:///{recordFileName}', echo=False)
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
