import time
import re
import os
import csv
import itertools
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

    filename = os.path.join(output_dir, f'{today_str}_google_reviews.csv')
    # 指定字段名
    fieldnames = ['review_date', 'review_text', 'review_rate', 'review_hotel', 'review_source']

    # 如果文件不存在，则创建文件并写入标题行
    if not os.path.exists(filename):
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    return filename



def scrape_reviews(browser,url,hotelname):
    browser.get(url)
    time.sleep(2)
    saved_reviews = []

    def switch_latest_sort():
        browser.execute_script("window.scrollBy(0, 500)") 
        sortedstroll = browser.find_element(By.XPATH,'//*[@id="reviews"]/c-wiz/c-wiz/div/div/div/div/div[3]/div/div[3]/span[1]/span/div/div[1]/div[1]/div[1]')
        sortedstroll.click()
        time.sleep(1)

        #switch review sort to latest
        Latest =  browser.find_element(By.XPATH,'//*[@id="reviews"]/c-wiz/c-wiz/div/div/div/div/div[3]/div/div[3]/span[1]/span/div[1]/div[2]/div[2]')
        Latest.click()
        time.sleep(3)  
                
    def scroll_website():

        def click_readmore(): #將網頁上的"閱讀完整內容"點開
            item = browser.find_elements(By.XPATH,'//*[@id="reviews"]/c-wiz/c-wiz/div/div/div/div/div[4]')#用來定位Read more按鈕
            for i in item:
                buttons = i.find_elements(By.CSS_SELECTOR,'span[jsname="kDNJsb"]')#找出所有的閱讀完整內容
                for button in buttons:
                    if button.text == "閱讀完整內容" or button.text == "閱讀更多" :
                        browser.execute_script("arguments[0].click();", button)
    #往下滑，直到一周後的評論
        should_continue = True 

        while should_continue:
            #終止條件
            comment_blocks = browser.find_elements(By.XPATH , '//div[@class="Svr5cf bKhjM"]')
            for comment_block in comment_blocks:                
                date = comment_block.find_element(By.XPATH, './/span[contains(@class, "iUtr1") and contains(@class, "CQYfx")]').text 
                if "1 週前" in date:
                    should_continue = False
                    print("Finish Scroll")
                    break
            
            browser.execute_script("window.scrollBy(0, 5000)")                        # scroll down 10000 pixels
            browser.execute_script("window.scrollBy(0, -200)")                         # scroll up by 200 pixels (if this is not done, new data will not be loaded)
            time.sleep(2)
            click_readmore() 
 
    
    switch_latest_sort()
    scroll_website()

    saved_reviews=[]
    validCount,invalidCount = 0,0
    comment_blocks = browser.find_elements(By.XPATH , '//div[@class="Svr5cf bKhjM"]')
    for comment_block in comment_blocks:
        review_dict = {
            'review_date': None,
            'review_text': None,
            'review_rate': None,
            'review_hotel': hotelname,
            'review_source':'Google'
        }
        try:           
            review_date  = comment_block.find_element(By.XPATH, './/span[contains(@class, "iUtr1") and contains(@class, "CQYfx")]').text
            if "1 週前" in review_date:
                print(f"Finish {hotelname}'s Scrape")
                print(f"Valid review: {validCount}")
                print(f"Invalid review: {invalidCount}")
                break
            review_dict['review_date'] = review_date #要把Google刪掉

            review_text = comment_block.find_element(By.XPATH, './/div[@class="STQFb eoY5cb"]//div[@class="K7oBsc"]/div/span').text
            review_dict['review_text'] = review_text

            review_rate = comment_block.find_element(By.CLASS_NAME, 'GDWaad').text
            review_dict['review_rate'] = review_rate # 5/5 -> 5

        except NoSuchElementException:
            invalidCount += 1
            continue
        
        saved_reviews.append(review_dict)
        validCount += 1

    return saved_reviews

def export_review(review_dicts,exportpath):
    #預處理date和rate後，再儲存

    def extract_chinese_review(comment):#剔除原始評論與google翻譯
        split_comment = comment.split("(原始評論)")
        if len(split_comment) > 1:
            chinese_content = split_comment[0].strip()
            chinese_content = chinese_content.replace("(由 Google 提供翻譯)", " ")
        else:
            chinese_content = comment
        chinese_content = chinese_content.replace("\n", " ")  # 在任何情况下都将换行转换为空格

        return chinese_content.strip()
    

    def clean_date_string(date_string):
        # 去除空格和非數字字元
        cleaned_string = re.sub(r'[^\d]', '', date_string)
        
        # 提取數字部分作為時間數量
        time_number = int(cleaned_string)
        
        # 判斷時間單位
        if '小時' in date_string:
            multiplier = 1
        elif '天' in date_string:
            multiplier = 24
        else:
            return None
        
        # 計算相對時間
        hours_ago = time_number * multiplier
        
        # 轉換為標準時間格式
        cleaned_date_string = (datetime.now() - timedelta(hours=hours_ago)).strftime('%Y-%m-%d')
        
        return cleaned_date_string


        
    # review_dict = {
    #         'review_date': None,
    #         'review_text': None,
    #         'review_rate': None,
    #         'review_hotel': hotelname,
    #         'review_source':'Google'
    #     }
    for review_dict in review_dicts: #預處理評論
        review_dict['review_text'] = extract_chinese_review(review_dict['review_text'])
        review_dict['review_date'] = clean_date_string(review_dict['review_date'])
        review_dict['review_rate'] = review_dict['review_rate'].split("/")[0]
    #將評論新增到當天的csv中
    with open(exportpath, mode='a', encoding='utf-8', newline='') as file:
        fieldnames = ['review_date', 'review_text', 'review_rate', 'review_hotel', 'review_source']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        for review_dict in review_dicts:
            writer.writerow(review_dict)


def main():
    
    browser = setup_selenium()
    filename = create_csv()

    # items = list(google_list.items())
    # item_key, item_value = items[7]  # ('飯店A', 'http://hotelA.com')

    for hotel_name, link in google_list.items():
        savedReviews = scrape_reviews(browser,link,hotel_name)
        export_review(savedReviews,filename)

    print(f"爬蟲{filename}已經結束")

    

    # for key,value in google_list.items():
    #     print(key)
    #     print(value)
    #export_review(savedReviews,item_key)


    # for hotel,link in google_list.items():
    #     savedReviews = scrape_reviews(browser,link,hotel)
    #     export_review(savedReviews,hotel)

    time.sleep(20)




if __name__ == '__main__':
    main()