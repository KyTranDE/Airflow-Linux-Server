from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.firefox.service import Service
from utils.process import extract_phone_numbers, extract_reviews, convert_to_date, append_data_to_json
import pandas as pd
import threading
import pytz
import time
import json
import os
import logging



def GetDataSelenium2Html(url):
    firefox_options = Options()
    # firefox_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    firefox_options.add_argument("--lang=vi")
    # firefox_options.add_argument("--remote-debugging-port=0")
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--log-level=3')
    firefox_options.page_load_strategy = 'eager'
    
    logging.getLogger('selenium').setLevel(logging.CRITICAL)
    if os.name == 'nt':
        log_path = 'NUL'
    else:
        log_path = '/dev/null'
    
    service = Service(log_path=log_path)
    driver = webdriver.Firefox(service = service, options=firefox_options)
    driver.get(url=url)

    driver.maximize_window()
    
    time.sleep(1)
    driver.execute_script("document.body.style.zoom='25%'")
    # html 1
    html = driver.page_source 
    # html 2
    try:
        div_element = driver.find_element(By.XPATH, "//div[@class='RWPxGd' and @role='tablist']")
    except NoSuchElementException:
        div_element = None

    if div_element:
        buttons = div_element.find_element(By.XPATH, '//button[@role="tab" and @class="hh2c6 " and @data-tab-index="1"]')
        if 'Reviews' in buttons.get_attribute('aria-label') or 'Bài đánh giá' in buttons.get_attribute('aria-label'):
            buttons.click()
            ele = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')))
            last_height = driver.execute_script("return document.body.scrollHeight",ele)

            while True:
                ele = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
                driver.execute_script('arguments[0].scrollBy(0, 80000);', ele)
                time.sleep(5)
                
                ele = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
                new_height = driver.execute_script("return arguments[0].scrollHeight", ele)
                if new_height == last_height:
                    break
                last_height = new_height       
                
            html2 = driver.page_source
            
        else:
            html2 = None
    else:
        html2 = None
            
    driver.quit()
    return html,html2

def GetDataFromBs4(html,html2,url):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}
    data['brand'] = 'maps'
    data['media'] = 'google_maps'
    data["created_at"]  = None
    data["hashtag"] = "#thaco"
    data['user_name'] = soup.find('h1').text if soup.find('h1') else ''
    data['user_handle'] =  '@' + soup.find('h1').text if soup.find('h1') else ''
    data['user_url'] = url
    data['user_id'] = 'id:'+soup.find('h1').text if soup.find('h1') else ''
    data['email'] = ''
    data['phone'] = extract_phone_numbers(soup.find('div', attrs={'class': 'm6QErb XiKgde'}).text)[0] if soup.find('div', attrs={'class': 'm6QErb XiKgde'}) else ''
    data['address'] = soup.find('div', attrs={'class': 'Io6YTe fontBodyMedium kR99db fdkmkc'}).text if soup.find('div', attrs={'class': 'Io6YTe fontBodyMedium kR99db fdkmkc'}) else ''
    data['view'] = 0

    if html2 != None:
        data['reaction'] = {
            'like': extract_reviews(soup.find_all('tr', attrs={'class': 'BHOKXe'})[0].get('aria-label')),
            'love': extract_reviews(soup.find_all('tr', attrs={'class': 'BHOKXe'})[1].get('aria-label')),
            'haha': extract_reviews(soup.find_all('tr', attrs={'class': 'BHOKXe'})[2].get('aria-label')),
            'wow': extract_reviews(soup.find_all('tr', attrs={'class': 'BHOKXe'})[3].get('aria-label')),
            'sad': extract_reviews(soup.find_all('tr', attrs={'class': 'BHOKXe'})[4].get('aria-label')),
            'angry': 0,
            'other': 0
        }
        data['comments'] = []
        soup2s = BeautifulSoup(html2, 'html.parser')
        for soup2  in soup2s.find_all('div', attrs={'class': 'jftiEf fontBodyMedium'}):
            comment = {
                    "created_at": convert_to_date(soup2.find('span', attrs={'class': 'rsqaWe'}).text).astimezone(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d %H:%M:%S") if soup2.find('span', attrs={'class': 'rsqaWe'}) else '',
                    "reply_to": "",
                    "user_name": soup2.find('div', attrs={'class': 'd4r55'}).text if soup2.find('div', attrs={'class': 'd4r55'}) else '',
                    "user_url": soup2.find('button', attrs={'class': 'al6Kxe'}).get('data-href') if soup2.find('button', attrs={'class': 'al6Kxe'}) else '',
                    "user_id": soup2.find('button', attrs={'class': 'al6Kxe'}).get('data-review-id') if soup2.find('button', attrs={'class': 'al6Kxe'}) else '',
                    "email": "",
                    "phone": "",
                    "address": "",
                    "content": soup2.find('span', attrs={'class': 'wiI7pd'}).text if soup2.find('span', attrs={'class': 'wiI7pd'}) else '',
                    "title": "",
                    "comment_url": "", #có thể lấy được nhưng mà tốn time nên để trống nào rảnh em fix sau hihihi:>
                    "reaction": {
                        "like": int(soup2.find('span', attrs={'class': 'pkWtMe'}).text) if soup2.find('span', attrs={'class': 'pkWtMe'}) else 0,
                        "love": 0,
                        "haha": 0,
                        "wow": 0,
                        "sad": 0,
                        "angry": 0,
                        "other": 0
                    }
                }
            data['comments'].append(comment)
    else:
        data['reaction'] = {
            'like': 0,
            'love': 0,
            'haha': 0,
            'wow': 0,
            'sad': 0,
            'angry': 0,
            'other': 0
        }
        data['comments'] = [
            {
                "created_at": "",
                "reply_to": "",
                "user_name": "",
                "user_url": "",
                "user_id": "",
                "email": "",
                "phone": "",
                "address": "",
                "content": "",
                "title": "",
                "comment_url": "",
                "reaction": {
                    "like": 0,
                    "love": 0,
                    "haha": 0,
                    "wow": 0,
                    "sad": 0,
                    "angry": 0,
                    "other": 0
                    }
                }
            ]
    
    return data

def process_url(url, data_file_path, lock):
    """
    Hàm này sẽ được gọi bởi mỗi luồng để xử lý một URL cụ thể.
    """
    try:
        html, html2 = GetDataSelenium2Html(url)
        data = GetDataFromBs4(html, html2, url)
        append_data_to_json(data_file_path, data, lock)
        logging.info(f'Done: {url}')
    except Exception as e:
        logging.error(f'Error processing {url}: {e}')

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='./loggs/app.log', filemode='a')
    
    df = pd.read_csv('data/datalink/list_maps.csv')
    list_url = df['link_maps'].tolist()
    
    data_file_path = '/home/tky/ky_ws/review/data/data.json'
    os.makedirs('/home/tky/ky_ws/review/data/', exist_ok=True)

    if not os.path.exists(data_file_path):
        with open(data_file_path, 'w', encoding='utf-8-sig') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    lock = threading.Lock()
    max_workers = 50 
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_url, url, data_file_path, lock) for url in list_url]
        for future in futures:
            try:
                future.result() 
            except Exception as e:
                logging.error(f'Error in thread: {e}')

    logging.info('All data has been processed.')