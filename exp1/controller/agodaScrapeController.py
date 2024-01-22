import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException)
from datetime import datetime
from dateutil.relativedelta import relativedelta


def initialize_browser(url):
    try:
        browser = webdriver.Edge()
        browser.get(url)
        time.sleep(2)
        return browser
    except (WebDriverException, TimeoutException, NoSuchElementException) as e:
        print(f"Error initializing Selenium: {str(e)}")
        raise


def switch_chinese(browser):
    # browser.execute_script("window.scrollBy(0, 500)")
    languageMenu = browser.find_element(
        By.XPATH, '//*[@id="reviewFilterSection"]/div[1]/div[3]')
    languageMenu.click()
    time.sleep(1)
    zhtw = browser.find_element(
        By.XPATH, '//*[@id="reviews-language-filter_list"]/ul/li[4]')
    zhtw.click()
    time.sleep(1)


def click_readmore(browser):
    try:
        read_more_button = browser.find_element(
            By.XPATH, '//*[@id="reviewSection"]/div[5]/button')
        read_more_button.click()
        time.sleep(1)
        return True
    except NoSuchElementException:
        return False


def parse_review_date(date_text):
    date_format = "%Y年%m月%d日"
    # 移除日期文字中的星期幾評價
    date_text = date_text.replace("評鑑日期：", "").replace("星期一", "").replace("星期二", "").replace("星期三", "").replace(
        "星期四", "").replace("星期五", "").replace("星期六", "").replace("星期日", "")
    # 解析日期文字
    return datetime.strptime(date_text, date_format)


def scroll_website(browser):
    should_continue = True
    while should_continue:
        # # 終止條件，超過一年的評論將會停止爬蟲
        # comments = browser.find_elements(By.CLASS_NAME, 'Review-comment')
        # for comment in comments:
        #     review_date = comment.find_element(
        #         By.CLASS_NAME, 'Review-statusBar-date').text
        #     if parse_review_date(review_date) < datetime.now() - relativedelta(years=1):
        #         should_continue = False
        #         break

        # 向下滾動頁面
        last_height = browser.execute_script(
            "return document.body.scrollHeight")
        browser.execute_script(
            "window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(2)

        # 嘗試點擊 "閱讀更多"。如果按鈕不存在或無法點擊，click_readmore 返回 False
        if not click_readmore(browser):
            new_height = browser.execute_script(
                "return document.body.scrollHeight")
            # 如果經過滾動和嘗試點擊後，頁面高度沒有改變，則認為已到達頁面底部
            if new_height == last_height:
                should_continue = False


def extract_reviews(browser, hotel_name):
    saved_reviews = []
    comments = browser.find_elements(By.CLASS_NAME, 'Review-comment')

    for comment in comments:
        try:
            review_date = comment.find_element(
                By.CLASS_NAME, 'Review-statusBar-date').text
            review_text = comment.find_element(
                By.CLASS_NAME, 'Review-comment-bodyText').text
            review_rate = comment.find_element(
                By.CLASS_NAME, 'Review-comment-leftScore').text

            review_dict = {
                'review_date': review_date,
                'review_text': review_text,
                'review_rate': review_rate,
                'review_hotel': hotel_name,
                'review_source': 'Agoda'
            }
            saved_reviews.append(review_dict)
        except NoSuchElementException:
            continue

    return saved_reviews


def scrape_reviews(url: str, hotel_name: str):
    browser = initialize_browser(url)
    switch_chinese(browser)
    scroll_website(browser)
    reviews = extract_reviews(browser, hotel_name)
    browser.quit()
    return reviews
