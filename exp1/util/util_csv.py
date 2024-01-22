import os
import csv
from datetime import datetime, timedelta


def create_csv(hotel, source):

    output_dir = f'./output/{source}/'
    today_str = datetime.today().strftime('%Y-%m-%d')
    platform = source

    # 检查 output 文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    exportpath = os.path.join(
        output_dir, f'{hotel}_{platform}_reviews_{today_str}.csv')
    # 指定字段名
    fieldnames = ['review_date', 'review_text',
                  'review_rate', 'review_hotel', 'review_source']

    # 如果文件不存在，则创建文件并写入标题行
    if not os.path.exists(exportpath):
        with open(exportpath, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    return exportpath
