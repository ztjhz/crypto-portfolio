from dotenv import load_dotenv
import os
import datetime

load_dotenv()
USERNAME = os.getenv("COIN_GECKO_USERNAME")
PASSWORD = os.getenv("COIN_GECKO_PASSWORD")
EXECUTABLE_PATH = os.getenv("CHROME_WEBDRIVER_EXECUTABLE_PATH")
DISPLAYPROFIT = False
CASHBACK = ["3% CASHBACK", "NETFLIX REBATE", "SPOTIFY REBATE", "CRYPTO PAY"]

readFileName = "crypto.db"
DATE = datetime.date.today().strftime('%d/%m/%Y')
record_date = datetime.date.today().strftime('%d-%m-%Y')
# Go back in time
# DATE = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d/%m/%Y')
# record_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d-%m-%Y')
readFileName = "crypto.db"
recordFolderName = f"Record/{datetime.date.today().strftime('%Y-%m')}"
recordFileName = f'{recordFolderName}/{record_date}.db'
averagePriceFileName = 'average_price.json'