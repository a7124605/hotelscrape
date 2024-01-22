import csv


def preProcessing(review_dicts):
    # 使用列表推導過濾掉 'review_text' 為 "客人沒有留下任何評語" 的評論
    processed_reviews = [
        review for review in review_dicts if review['review_text'] != "客人沒有留下任何評語。"]
    return processed_reviews


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
