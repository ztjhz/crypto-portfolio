from dotenv import load_dotenv
import os
import datetime

load_dotenv()
USERNAME = os.getenv("COIN_GECKO_USERNAME")
PASSWORD = os.getenv("COIN_GECKO_PASSWORD")
EXECUTABLE_PATH = os.getenv("CHROME_WEBDRIVER_EXECUTABLE_PATH")
DISPLAY_PROFIT = False
CASHBACK = ["3% CASHBACK", "NETFLIX REBATE", "SPOTIFY REBATE", "CRYPTO PAY"]

READ_FILE_NAME = "crypto.db"
DATE = datetime.date.today().strftime('%d/%m/%Y')
RECORD_DATE = datetime.date.today().strftime('%d-%m-%Y')
# Go back in time
# DATE = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d/%m/%Y')
# RECORD_DATE = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d-%m-%Y')
READ_FILE_NAME = "crypto.db"
RECORD_FOLDER_NAME = f"Record/{datetime.date.today().strftime('%Y-%m')}"
RECORD_FILE_NAME = f'{RECORD_FOLDER_NAME}/{RECORD_DATE}.db'
AVERAGE_PRICE_FILE_NAME = 'average_price.json'
