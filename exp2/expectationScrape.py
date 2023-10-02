import time
import re
import os
import csv
from datetime import datetime, timedelta


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException)
from hotels import google_list


def setup_selenium():
    try:
        browser = webdriver.Edge()
        browser.get('https://www.google.com/')
    except (WebDriverException, TimeoutException, NoSuchElementException) as e:
        print(f"Error at init Selenium: {str(e)}")
        raise

    return browser



def create_csv():

    output_dir = 'output'
    today_str = datetime.today().strftime('%Y-%m-%d')

    # 检查 output 文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = os.path.join(output_dir, f'{today_str}_google_overall_rate.csv')
    # 指定字段名
    fieldnames = ['date', 'overall_rate', 'hotel', 'source']

    # 如果文件不存在，则创建文件并写入标题行
    if not os.path.exists(filename):
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    return filename

def scrape_overallRate(browser,url,hotelname):    
    try:
        browser.get(url)
        time.sleep(2)
        rate = browser.find_element(By.XPATH,'//*[@id="reviews"]/c-wiz/c-wiz/div/div/div/div/div[1]/div/div/div[1]/div[1]').text
        print(f"{hotelname}'s rate is {rate}")
        return rate
    except NoSuchElementException:
        print(f"Could not find the rate for {hotelname}")
        return None  


def main():
    browser = setup_selenium()
    filename = create_csv()
    allHotelrates = {}

    for hotelname,link in google_list.items():
        rate = scrape_overallRate(browser,link,hotelname)
        allHotelrates[hotelname] = rate

    with open(filename, mode='a', encoding='utf-8', newline='') as file:
        fieldnames = ['date', 'overall_rate', 'hotel', 'source']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        today_str = datetime.today().strftime('%Y-%m-%d')  # 获取当前日期
        for hotel, rate in allHotelrates.items():
            row_dict = {'date': today_str, 'overall_rate': rate, 'hotel': hotel, 'source': 'Google'}
            writer.writerow(row_dict)
    
    print("Expectation crawler finished")
    

if __name__ == '__main__':
    main()


