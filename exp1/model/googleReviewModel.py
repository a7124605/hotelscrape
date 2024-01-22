import re
import csv
from datetime import datetime, timedelta


def extract_chinese_review(comment):  # 剔除原始評論與google翻譯
    split_comment = comment.split("(原始評論)")
    if len(split_comment) > 1:
        chinese_content = split_comment[0].strip()
        chinese_content = chinese_content.replace("(由 Google 提供翻譯)", " ")
    else:
        chinese_content = comment
    chinese_content = chinese_content.replace("\n", " ")  # 在任何情况下都将换行转换为空格

    return chinese_content.strip()


def convert_google_date(date_string):
    # 去除空格和非數字字元
    cleaned_string = re.sub(r'[^\d]', '', date_string)
    time_number = int(cleaned_string)
    current_date = datetime.now()

    # 判斷時間單位並計算相對時間
    if '小時' in date_string:
        return_date = current_date - timedelta(hours=time_number)
    elif '天' in date_string:
        return_date = current_date - timedelta(days=time_number)
    elif '週' in date_string:
        return_date = current_date - timedelta(weeks=time_number)
    elif '月' in date_string:
        return_date = current_date - \
            timedelta(days=time_number * 30)  # 假設每月30天
    elif '年' in date_string:
        return_date = current_date - \
            timedelta(days=time_number * 365)  # 假設每年365天
    else:
        return None

    # 轉換為標準時間格式
    return return_date.strftime('%Y-%m-%d')


def preProcessing(review_dicts):
    for review_dict in review_dicts:  # 預處理評論
        review_dict['review_text'] = extract_chinese_review(
            review_dict['review_text'])
        review_dict['review_date'] = convert_google_date(
            review_dict['review_date'])
        review_dict['review_rate'] = review_dict['review_rate'].split("/")[0]
    return review_dicts


def writeInCsv(processedReviews, exportpath):
    with open(exportpath, mode='a', encoding='utf-8', newline='') as file:
        fieldnames = ['review_date', 'review_text',
                      'review_rate', 'review_hotel', 'review_source']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        for processedReview in processedReviews:
            writer.writerow(processedReview)


def export_reviews(review_dicts, exportpath):
    processedReviews = preProcessing(review_dicts)
    writeInCsv(processedReviews, exportpath)
    print(f"{exportpath} have been export!")
