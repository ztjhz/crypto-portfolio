from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

from src.env.main import USERNAME, PASSWORD, EXECUTABLE_PATH


def updateCoinGecko(symbols, symbol_total_df, symbol_cost_df):
    opts = Options()
    opts.headless = False

    username = USERNAME
    password = PASSWORD
    executable_path = EXECUTABLE_PATH
    portfolio_url = 'https://www.coingecko.com/en/portfolio'

    browser = Chrome(options=opts, executable_path=executable_path)
    browser.implicitly_wait(10)

    browser.get(portfolio_url)

    # accept cookies
    browser.find_element_by_xpath(
        "//button[@data-action='click->cookie-note#accept']").click()

    # Log in
    browser.find_element_by_xpath(
        "//button[@data-target = '#signInModal']").click()
    browser.find_element_by_id('signInEmail').send_keys(f'{username}')
    browser.find_element_by_id('signInPassword').send_keys(f'{password}')
    browser.find_element_by_xpath("//input[@value = 'Login']").submit()

    updated = False

    while not updated:
        if browser.current_url != portfolio_url:
            browser.get(portfolio_url)
        # Get links to the different coins
        elements = browser.find_elements_by_xpath(
            "//td[@class = 'text-right col-gecko no-wrap holding-val']/a")

        all_links = {}
        quantity_list = []
        unstarList = []
        for element in elements:
            link = element.get_attribute('href')
            oldQuantity, symbol = element.find_elements_by_xpath(
                ".//div[@class='text-black']/span")[3].text.split(' ')

            if symbol not in symbols:
                unstarList.append(symbol)
                continue
            newQuantity = str(symbol_total_df[symbol])
            price = symbol_cost_df[symbol]
            all_links[link] = [symbol, newQuantity, price]
            if oldQuantity != newQuantity:
                quantity_list.append(symbol)

        for symbol in unstarList:
            unstarButton = browser.find_element_by_xpath(
                f"//td[@class='pl-1 pr-0']/i[@data-coin-symbol='{symbol.lower()}']"
            )
            unstarButton.click()
            confirmationButton = browser.find_element_by_xpath(
                "//button[@id='unfavourite-coin-confirm-button']")
            confirmationButton.click()
            while len(
                    browser.find_elements_by_xpath(
                        f"//td[@class='pl-1 pr-0']/i[@data-coin-symbol='{symbol.lower()}']"
                    )) != 0:
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
                edit_button = browser.find_element_by_xpath(
                    "//td/a[@class='text-primary']")
                edit_button.click()
                transaction_type = 'edit'
                current_quantity = browser.find_element_by_xpath(
                    "//td[@class='text-right']/span[@class='text-green']"
                ).text.lstrip("+")

            except NoSuchElementException:
                # add new transaction
                new_transaction_button = browser.find_element_by_xpath(
                    "//div/a[@data-action='click->portfolio-coin-transactions-new#updateCoinIdValue']"
                )
                new_transaction_button.click()
                transaction_type = 'new'
                current_quantity = 0

            # enter new value into quantity
            quantity_field = browser.find_element_by_xpath(
                f"//input[@id='portfolio-coin-transactions-{transaction_type}_portfolio_coin_transaction_quantity']"
            )
            if current_quantity != quantity:
                quantity_field.clear()
                quantity_field.send_keys(quantity)
                update_quantity = True
            price_element = browser.find_element_by_id(
                f"portfolio-coin-transactions-{transaction_type}_portfolio_coin_transaction_price"
            )
            WebDriverWait(
                browser,
                10).until(lambda x: price_element.get_attribute('value') != '')
            current_price = float(price_element.get_attribute('value'))
            if current_price != price:
                browser.execute_script(
                    f"document.getElementById('portfolio-coin-transactions-{transaction_type}_portfolio_coin_transaction_price').value={price}"
                )
                update_price = True

            if update_price == True or update_quantity == True:
                quantity_field.send_keys(Keys.ENTER)
            if update_price == True and update_quantity == True:
                print(
                    f'{quantity} {coin_symbol} (${price}) has been updated on CoinGecko!'
                )
            elif update_price == True:
                print(
                    f'{coin_symbol} (${price}) has been updated on CoinGecko!')
            elif update_quantity == True:
                print(
                    f'{quantity} {coin_symbol} has been updated on CoinGecko!')

        updated = True

    browser.quit()
