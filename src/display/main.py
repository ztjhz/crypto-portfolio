import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import webbrowser
import os


def displayCoinsAvailable(COINS):
    print('Coins available: ')
    for i in range(len(COINS)):
        print(f'{i}: {COINS[i]}')


def displayPlatformsAvailable(PLATFORM):
    print('Platform available: ')
    for i in range(len(PLATFORM)):
        print(f'{i}: {PLATFORM[i]}')


def displayTypesAvailable(TYPE):
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
    print('gg. Display Graph (web)')


def printHeading(heading):
    print("-" * len(heading))
    print(heading)
    print("-" * len(heading))


def displayPortfolioChange(change_df):
    heading = "Portfolio change over time:"
    print()
    printHeading(heading)
    print(change_df)


def display_graph(record_index, record_total_pl):
    dates = pd.Series(x for x in record_index)
    tick_interval = int(len(record_index) / 26)

    matplotlib.style.use('ggplot')

    fg, ax = plt.subplots(figsize=(12, 7))
    ax.plot(dates, record_total_pl / 1.33, label="1")
    #ax.plot(dates, record_df["PORTFOLIO VALUE"], label="2", linestyle="dashed")

    ax.set_xlabel("Date")
    ax.set_ylabel("P/L (USD)")
    ax.set_title("P/L Over Time")

    plt.xticks(dates[::tick_interval])
    plt.tight_layout()
    fg.autofmt_xdate()
    plt.show()


def display_graph_web(record_index, record_total_pl,
                      record_total_deposited_withdrawn,
                      record_portfolio_value):
    labels = [date for date in record_index]
    data_sgd = [val for val in record_total_pl]
    total_deposited_sgd = []
    total_withdrawn_sgd = []
    portfolio_sgd = [val for val in record_portfolio_value]

    # net deposit = total deposited - total withdrawn
    net_deposit = []
    for _, row in record_total_deposited_withdrawn.iterrows():
        d = row['TOTAL DEPOSITED']
        w = row['TOTAL WITHDRAWN']
        total_deposited_sgd.append(d)
        total_withdrawn_sgd.append(w)
        net_deposit.append(d - w)

    with open("web_src/data.js", "w") as f:
        f.write(
            f"const data = {{labels:{labels},data_sgd:{data_sgd},total_deposited_sgd:{total_deposited_sgd},total_withdrawn_sgd:{total_withdrawn_sgd},net_deposit:{net_deposit},portfolio_sgd:{portfolio_sgd}}}"
        )

    webbrowser.get("windows-default").open(f"{os.getcwd()}/web_src/graph.html")


def displayProfitPerCoin(getProfitPerCoin, inactive=False):
    printHeading('Profit Per Coin:')
    profit_per_coin = getProfitPerCoin(all=True)
    for v in profit_per_coin.values():
        if v['PROFIT'] != "NA":
            v['PROFIT'] = "{:.2f}".format(v['PROFIT'])
        if v['%'] != 'NA':
            v['%'] = float("{:.2f}".format(v['%']))
    df = pd.DataFrame(profit_per_coin).transpose()
    # sort by %
    display_df = pd.DataFrame(df[(df['%'] != 'NA')
                                 & (df['Active'] == True)].sort_values(
                                     by='%', ascending=False))
    # sort by profit for those with NA %
    display_df = display_df.append(
        df[(df['%'] == 'NA') & (df['PROFIT'] != 'NA') &
           (df['Active'] == True)].sort_values(by='PROFIT', ascending=False))

    display_df.drop("Active", axis=1, inplace=True)
    #df.sort_values(by='%', inplace=True, ascending=False)
    #df.rename_axis("COIN", inplace=True)
    pd.options.display.max_rows = len(profit_per_coin)
    print(display_df)

    if inactive:
        print()
        printHeading("Inactive coins:")
        print(df[(df['Active'] == False) & (df['%'] != 'NA')].sort_values(
            by='PROFIT', ascending=True).drop("Active", axis=1))


def displayPortfolioSummary(data, total_dict, USDSGD):
    """ 
    Display summary of portfolio (Deposit, Withdrawal and Profit)

    Display change of profit over time in days (1, 7, 30, 60, 90, 120, 180, 270, 365)
    """
    totalDeposited = data.getTotalDeposit()
    totalWithDrawn = data.getTotalWithdrawal()
    currentPL = totalWithDrawn + total_dict['sgd'] - totalDeposited
    percentagePL = (currentPL / totalDeposited) * 100
    SGDheading = "Portfolio summary in SGD:"
    USDheading = 'Portfolio summary in USD:'

    print('{:<40s}'.format("-" * len(SGDheading)), end='')
    print('{:<40s}'.format("-" * len(USDheading)))

    print('{:<40s}'.format(SGDheading), end='')
    print('{:<40s}'.format(USDheading))

    print('{:<40s}'.format("-" * len(SGDheading)), end='')
    print('{:<40s}'.format("-" * len(USDheading)))

    print('{:<40s}'.format('Total deposited: ${:.2f}'.format(totalDeposited)),
          end='')
    print('{:<40s}'.format('Total deposited: ${:.2f}'.format(totalDeposited /
                                                             USDSGD)))

    print('{:<40s}'.format('Total withdrawn: ${:.2f}'.format(totalWithDrawn)),
          end='')
    print('{:<40s}'.format('Total withdrawn: ${:.2f}'.format(totalWithDrawn /
                                                             USDSGD)))

    print('{:<40s}'.format('Portfolio value: ${:.2f}'.format(
        total_dict['sgd'])),
          end='')
    print('{:<40s}'.format('Portfolio value: ${:.2f}'.format(
        total_dict['usd'])))

    print('{:<40s}'.format('Total P/L: ${:.2f} ({:.2f}%)'.format(
        totalWithDrawn + total_dict['sgd'] - totalDeposited, percentagePL)),
          end='')
    print('{:<40s}'.format('Total P/L: ${:.2f} ({:.2f}%)'.format(
        (totalWithDrawn / USDSGD) + total_dict['usd'] -
        (totalDeposited / USDSGD), percentagePL)))

    change_df = data.getPortfolioChange(percentagePL, currentPL)
    displayPortfolioChange(change_df)


def displayPortfolioDF(price_df, coin_count, currency, total):
    """ Display portfolio df (For option 0) """
    print(price_df)

    pd.options.display.max_rows = coin_count
    pd.reset_option('precision')
    heading = 'Total in {}: ${:.2f}'.format(currency.upper(), total)
    print("-" * len(heading))
    print(heading)
    print("-" * len(heading))
    print()