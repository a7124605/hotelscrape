import csv
from datetime import datetime, timedelta


def convert_agoda_date(date_text):
    # 定義原始日期文字的格式
    date_format = "%Y年%m月%d日"
    try:
        # 移除日期文字中的星期幾評價
        date_text = date_text.replace("評鑑日期：", "").replace("星期一", "").replace("星期二", "").replace("星期三", "").replace(
            "星期四", "").replace("星期五", "").replace("星期六", "").replace("星期日", "")
        # 解析日期文字
        dateString = datetime.strptime(date_text, date_format)
        # 轉換成所需的格式
        formatted_date = dateString.strftime("%Y-%m-%d")
        return formatted_date
    except ValueError:
        # 無法解析日期，返回預設值
        return None


def preProcessing(review_dicts):
    for review_dict in review_dicts:  # 預處理評論
        review_dict['review_date'] = convert_agoda_date(
            review_dict['review_date'])
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
