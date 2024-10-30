from selenium import webdriver
import time
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import random
import pandas as pd

def gradual_zoom_out(driver, start_zoom=1.0, end_zoom=0.5, step=0.05, delay=0.1):
    current_zoom = start_zoom
    while current_zoom > end_zoom:
        zoom_percentage = f"{current_zoom * 100}%"
        driver.execute_script(f"document.body.style.zoom='{zoom_percentage}'")
        time.sleep(delay)
        current_zoom -= step
        if current_zoom < end_zoom:
            current_zoom = end_zoom
    driver.execute_script(f"document.body.style.zoom='{end_zoom * 100}%'")

def set_random_user_agent_chrome():
    ua = UserAgent()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    chrome_options = Options()
    # chrome_options.add_argument(f"--user-agent={user_agent}")
    # chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--ignore-ssl-errors')
    # chrome_options.add_argument('--allow-insecure-localhost')
    # chrome_options.add_argument('--disable-web-security')
    # chrome_options.add_argument('--allow-running-insecure-content')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument("--start-maximized")
    # run ở chế độ headless
    chrome_options.add_argument("--headless")
    return chrome_options

def Crawl(chrome_options) :
    driver = webdriver.Chrome(options = chrome_options)
    driver.get('https://www.google.com/maps/search/thaco+/')
    time.sleep(random.randint(1, 5))
    # gradual_zoom_out(driver, start_zoom=1.0, end_zoom=0.5, step=0.05, delay=0.1)
    driver.maximize_window()
    time.sleep(random.randint(1, 5))

    while True:
        time.sleep(random.randint(1, 5))
        results = driver.find_elements(By.CLASS_NAME, 'hfpxzc')
        driver.execute_script("return arguments[0].scrollIntoView();", results[-1])
        page_text = driver.find_element(by=By.TAG_NAME, value='body').text
        endliststring="You've reached the end of the list."
        if endliststring not in page_text:
            driver.execute_script("return arguments[0].scrollIntoView();", results[-1])
        else:
            break
    driver.execute_script("return arguments[0].scrollIntoView();", results[-1])
    
    list_href = []
    for i in driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]'):
        list_href.append(i.get_attribute('href'))
    
    
    
    df = pd.DataFrame({'link_maps':list_href})
    df.to_csv('list_maps.csv', index=False)

    driver.quit()

if __name__ == '__main__':
    
    Crawl(set_random_user_agent_chrome())

