#!/usr/bin/python
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


def collecting_data_from_table(browser, action):
    header = browser.find_element(By.TAG_NAME, 'header')
    market_data = header.find_element(By.ID, 'link_2')    
    action.move_to_element(market_data).perform()
    browser.implicitly_wait(10)

    #Переходим по ссылке
    browser.delete_all_cookies()
    header.find_element(By.LINK_TEXT, 'Pre-Open Market').click() 
    time.sleep(5)

    #Получаем данные из таблицы
    table_body = browser.find_element(By.TAG_NAME, 'tbody')
    rows = table_body.find_elements(By.TAG_NAME, 'tr')

    data = [['name', 'price']]
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        value = [i.text for i in cols]
        data.append([value[1], value[8]])

    with open('final_price.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def imitation_of_user_actions(browser, action):
    #Скролл по странице 
    action.scroll_by_amount(0, 150).perform()
    time.sleep(5)

    #Настройки таблицы
    table_settings = browser.find_element(By.CLASS_NAME, 'sortby_showing')
    select = Select(table_settings.find_element(By.ID, 'sel-Pre-Open-Market'))
    select.select_by_value('ALL')
    time.sleep(5)
    table_settings.find_element(By.XPATH, '//label[@id="market-lakh"]').click()
    time.sleep(3)

    #Cкролл до конца таблицы
    table = browser.find_element(By.TAG_NAME, 'table')
    end_table = table.find_element(By.XPATH, '//tr/td[@id="total"]')
    time.sleep(2)
    action.scroll_to_element(end_table).perform()
    time.sleep(3)

    end_scroll = browser.find_element(By.CLASS_NAME, 'note_container')
    action.scroll_to_element(end_scroll).perform()
    time.sleep(5)


def main():
    URL = 'https://www.nseindia.com/'

    #Настройка драйвера и пользователя
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled') 
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    options.add_argument('accept-language=en-US,en;q=0.9')

    options.add_argument("--start-maximized")
    browser = webdriver.Chrome(options=options)

    try:        
        browser.get(URL)
        browser.implicitly_wait(10)

        action = ActionChains(browser)
        collecting_data_from_table(browser, action)
        imitation_of_user_actions(browser, action)       

    except Exception as _ex:
        print(_ex)
    finally:        
        browser.close()
        browser.quit()


if __name__ == '__main__':
    main()
