import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException)
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import datetime
from dateutil.relativedelta import relativedelta


def initialize_browser(url):
    try:
        url = url + "#tab-reviews"
        browser = webdriver.Edge()
        browser.get(url)
        time.sleep(2)
        return browser
    except (WebDriverException, TimeoutException, NoSuchElementException) as e:
        print(f"Error initializing Selenium: {str(e)}")
        raise


def switchNewest(browser):
    wait = WebDriverWait(browser, 10)
    select_element = wait.until(
        EC.element_to_be_clickable((By.ID, "review_sort")))
    # 創建 Select 對象
    select_object = Select(select_element)
    # 選擇下拉選單中的特定選項
    select_object.select_by_value("f_recent_desc")
    time.sleep(3)


def switchZh(browser):
    wait = WebDriverWait(browser, 10)
    language_dropdown_button = wait.until(
        EC.element_to_be_clickable((By.ID, "review_lang_filter_dropdown")))
    language_dropdown_button.click()
    # 等待下拉選單出現
    wait.until(EC.visibility_of_element_located((By.ID, "review_lang_filter")))
    # 定位中文選項按鈕並點擊
    chinese_option_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@data-value='zh']")))
    chinese_option_button.click()
    time.sleep(3)


def changePage(browser):
    try:
        wait = WebDriverWait(browser, 10)
        next_page_button = wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'pagenext')))

        if next_page_button:
            next_page_button.click()
            time.sleep(2)  # 等待新頁面加載
            return True
        else:
            return False
    except NoSuchElementException:
        print("No more pages or error in page navigation.")
        return False


def parse_review_date(date_str):
    date_format = "%Y 年 %m 月 %d 日"
    try:
        date_text = date_str.replace("留下評語", "").strip()
        return datetime.datetime.strptime(date_text, date_format)
    except ValueError:
        print("Date Trans Error")
        return None


def extract_reviews(browser, hotel_name):
    saved_reviews = []
    should_continue = True

    while should_continue:

        comments = browser.find_elements(
            By.CLASS_NAME, "c-review-block")

        for comment in comments:
            try:

                review_date = comment.find_element(
                    By.XPATH, '//*[@id="review_list_page_container"]/ul/li[4]/div/div[2]/div[2]/div[1]/span').text
                review_date = parse_review_date(review_date)

                # 超過1年的評論會終止迴圈
                if review_date != None and review_date < datetime.datetime.now() - relativedelta(years=1):
                    should_continue = False
                    break

                review_contents = comment.find_elements(
                    By.CLASS_NAME, "c-review__body")
                review_text = ''.join(
                    [content.text for content in review_contents])

                review_dict = {
                    'review_date': review_date.strftime("%Y-%m-%d") if review_date is not None else 'None',
                    'review_text': review_text,
                    'review_rate': 10,
                    'review_hotel': hotel_name,
                    'review_source': 'Booking.com'
                }
                saved_reviews.append(review_dict)

            except NoSuchElementException:
                continue

        if not changePage(browser):  # Finished
            print("Error at changePage")
            break

    return saved_reviews


def scrape_reviews(url: str, hotel_name: str):
    browser = initialize_browser(url)
    switchNewest(browser)
    switchZh(browser)

    reviews = extract_reviews(browser, hotel_name)
    browser.quit()
    return reviews
