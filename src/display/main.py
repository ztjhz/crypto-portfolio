import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


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


def display_graph(record_df):
    dates = pd.Series(x for x in record_df.index)
    tick_interval = int(len(record_df.index) / 26)

    matplotlib.style.use('ggplot')

    fg, ax = plt.subplots(figsize=(12, 7))
    ax.plot(dates, record_df["TOTAL P/L"] / 1.33, label="1")
    #ax.plot(dates, record_df["PORTFOLIO VALUE"], label="2", linestyle="dashed")

    ax.set_xlabel("Date")
    ax.set_ylabel("P/L (USD)")
    ax.set_title("P/L Over Time")

    plt.xticks(dates[::tick_interval])
    plt.tight_layout()
    fg.autofmt_xdate()
    plt.show()