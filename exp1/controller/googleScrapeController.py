import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException)


def initialize_browser(url: str):
    try:
        browser = webdriver.Edge()
        browser.get(url)
        time.sleep(2)
        return browser
    except (WebDriverException, TimeoutException, NoSuchElementException) as e:
        print(f"Error initializing Selenium: {str(e)}")
        raise


def scroll_and_click_read_more(browser, end_time: str):
    switch_latest_sort(browser)
    scroll_website(browser, end_time)


def switch_latest_sort(browser):
    browser.execute_script("window.scrollBy(0, 500)")
    sortedstroll = browser.find_element(
        By.XPATH, '//*[@id="reviews"]/c-wiz/c-wiz/div/div/div/div/div[3]/div/div[3]/span[1]/span/div/div[1]/div[1]/div[1]')
    sortedstroll.click()
    time.sleep(1)

    # switch review sort to latest
    Latest = browser.find_element(
        By.XPATH, '//*[@id="reviews"]/c-wiz/c-wiz/div/div/div/div/div[3]/div/div[3]/span[1]/span/div[1]/div[2]/div[2]')
    Latest.click()
    time.sleep(3)


def click_readmore(browser):
    # 將網頁上的"閱讀完整內容"點開
    item = browser.find_elements(
        By.XPATH, '//*[@id="reviews"]/c-wiz/c-wiz/div/div/div/div/div[4]')  # 用來定位Read more按鈕
    for i in item:
        buttons = i.find_elements(
            By.CSS_SELECTOR, 'span[jsname="kDNJsb"]')  # 找出所有的閱讀完整內容
        for button in buttons:
            if button.text == "閱讀完整內容" or button.text == "閱讀更多":
                browser.execute_script("arguments[0].click();", button)


def scroll_website(browser, end_time):
    # 往下滑，直到一周後的評論
    should_continue = True

    while should_continue:
        # 終止條件
        comment_blocks = browser.find_elements(
            By.XPATH, '//div[@class="Svr5cf bKhjM"]')
        for comment_block in comment_blocks:
            date = comment_block.find_element(
                By.XPATH, './/span[contains(@class, "iUtr1") and contains(@class, "CQYfx")]').text
            if end_time in date:
                should_continue = False
                print("Finish Scroll")
                break

        # scroll down 10000 pixels
        browser.execute_script("window.scrollBy(0, 5000)")
        # scroll up by 200 pixels (if this is not done, new data will not be loaded)
        browser.execute_script("window.scrollBy(0, -200)")
        time.sleep(1)
        click_readmore(browser)


def extract_reviews(browser, hotelname: str, end_time: str):
    saved_reviews = []
    validCount, invalidCount = 0, 0

    comment_blocks = browser.find_elements(
        By.XPATH, '//div[@class="Svr5cf bKhjM"]')
    for comment_block in comment_blocks:
        review_dict = {
            'review_date': None,
            'review_text': None,
            'review_rate': None,
            'review_hotel': hotelname,
            'review_source': 'Google'
        }
        try:
            review_date = comment_block.find_element(
                By.XPATH, './/span[contains(@class, "iUtr1") and contains(@class, "CQYfx")]').text

            if end_time in review_date:
                print(f"Finish {hotelname}'s Scrape")
                print(f"Valid review: {validCount}")
                print(f"Invalid review: {invalidCount}")
                break

            review_dict['review_date'] = review_date  # 要把Google刪掉
            review_text = comment_block.find_element(
                By.XPATH, './/div[@class="STQFb eoY5cb"]//div[@class="K7oBsc"]/div/span').text
            review_dict['review_text'] = review_text
            review_rate = comment_block.find_element(
                By.CLASS_NAME, 'GDWaad').text
            review_dict['review_rate'] = review_rate  # 5/5 -> 5

        except NoSuchElementException:
            invalidCount += 1
            continue

        saved_reviews.append(review_dict)
        validCount += 1

    return saved_reviews


def scrape_reviews(url: str, hotelname: str, end_time: str):
    browser = initialize_browser(url)
    scroll_and_click_read_more(browser, end_time)
    reviews = extract_reviews(browser, hotelname, end_time)
    browser.quit()
    return reviews
