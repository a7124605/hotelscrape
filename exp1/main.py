import json
from util.util_csv import create_csv
from controller.googleScrapeController import scrape_reviews as googleScrape
from controller.agodaScrapeController import scrape_reviews as agodaScrape
from controller.bkcomScrapeController import scrape_reviews as bkcomScrape
from model.googleReviewModel import export_reviews as googleExports
from model.agodaReviewModel import export_reviews as agodaExports
from model.bkcomReviewModel import export_reviews as bkcomExports


def main():
    with open('./util/hotels.json', 'r', encoding='utf-8') as file:
        hotels_list = json.load(file)

    for hotel in hotels_list:
        hotel_name = hotel['hotel_name']
        google_url = hotel['urls']['google']
        agoda_url = hotel['urls']['agoda']
        bkcom_url = hotel['urls']['bkcom']

        # # google Scrape
        # if google_url and google_url != "None":
        #     exportpath_google = create_csv(hotel_name, "google")
        #     google_reviews = googleScrape(google_url, hotel_name, "1 年前")
        #     googleExports(google_reviews, exportpath_google)
        #     print(f'{hotel_name}"s google review has already scraped')

        # Agoda Scrape
        if agoda_url and agoda_url != "None":
            exportpath_agoda = create_csv(hotel_name, "agoda")
            agoda_reviews = agodaScrape(agoda_url, hotel_name)
            agodaExports(agoda_reviews, exportpath_agoda)
            print(f'{hotel_name}"s agoda review has already scraped')

        # # Booking.com Scrape
        # if bkcom_url and bkcom_url != "None":
        #     exportpath_bkcom = create_csv(hotel_name, "bkcom")
        #     bkcom_reviews = bkcomScrape(bkcom_url, hotel_name)
        #     bkcomExports(bkcom_reviews, exportpath_bkcom)


main()
