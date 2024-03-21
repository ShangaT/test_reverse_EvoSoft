#!/usr/bin/python
import os
import time
import pickle
import logging
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from authentication_file import login, password

logging.basicConfig(level=logging.INFO)

def first_entry(browser):
    url_login = 'https://twitter.com/i/flow/login/'
    browser.get(url_login)
    browser.implicitly_wait(10)

    login_input = browser.find_element(By.XPATH, '//input[@autocomplete="username"]')
    login_input.send_keys(login)
    time.sleep(2)
    login_input.clear()
    login_input.send_keys(Keys.ENTER)
    time.sleep(20)

    password_input = browser.find_element(By.XPATH, '//input[@autocomplete="current-password"]')
    password_input.send_keys(password)
    time.sleep(2)
    password_input.clear()
    password_input.send_keys(Keys.ENTER)
    time.sleep(20)

    pickle.dump(browser.get_cookies(), open('cookies', 'wb'))


#прослушиваем сеть и находим нужный запрос
def wiretapping_network(browser):
    browser.execute_cdp_cmd('Network.enable', {})
    log_entries = browser.get_log("performance")
    
    for entry in log_entries:
        message_obj = json.loads(entry.get("message"))
        message = message_obj.get("message")
        method = message.get("method")

        if method == 'Network.responseReceived':
            response_url = message.get('params',{}).get('response',{}).get('url','')
            request_id = message.get('params', {}).get('requestId', '')
            
            if "UserTweets" in response_url:
                response = browser.execute_cdp_cmd('Network.getResponseBody',{'requestId':request_id})
                response_body = response.get('body','')

                body_json = json.loads(response_body)   
                return body_json


#находим тивитты и их текст
def data_filtering(data):
    entries = data['data']['user']['result']['timeline_v2']['timeline']['instructions'][2]['entries']
    #count_tweets = 0
    list_tweets = [['created_at', 'link']]

    for i in range(len(entries)):    
        entry_id = entries[i]['entryId']

        #поиск твиттов
        if entry_id.startswith('tweet'):
            #count_tweets += 1
            tweet = entries[i]['content']
            tweet_info = tweet['itemContent']['tweet_results']['result']['legacy']

            date = tweet_info['created_at']
            link = 'https://twitter.com/elonmusk/status/' + tweet_info['id_str']
            list_tweets.append([date, link])

            #исключаем ретвитты, так как они не содержат текста от того, кто делает ретвитт
            if 'retweeted_status_result' not in tweet_info:
                text_tweet = tweet_info['full_text']
                words = text_tweet.split()
                filtered_words = [word for word in words if not word.lower().startswith('https://t.co/')]
                clean_text = ' '.join(filtered_words)                                

                #исключаем твитты без текста
                if clean_text != '': logging.info(clean_text)

        if len(list_tweets) == 11: break

    with open('list_tweets.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(list_tweets)


def main():
    options = Options()
    options.add_experimental_option('detach',True)
    options.add_argument('--enable-logging')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    options.add_argument('--disable-blink-features=AutomationControlled') 
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    options.add_argument('accept-language=en-US,en;q=0.9')

    options.add_argument("--start-maximized")
    browser = webdriver.Chrome(options=options)

    try:
        #проходим аутентификацию, если неоткуда взять cookies
        if os.path.exists('cookies') == False:
            first_entry(browser)

        cookies = pickle.load(open('cookies', 'rb'))

        browser.get('https://twitter.com/')
        for cookie in cookies:
            browser.add_cookie(cookie)
        time.sleep(5)

        browser.get('https://twitter.com/elonmusk')
        time.sleep(10)

        content = wiretapping_network(browser)
        data_filtering(content)

    except Exception as _ex:
        print(_ex)
    finally:        
        browser.close()
        browser.quit()


if __name__ == '__main__':
    main()
