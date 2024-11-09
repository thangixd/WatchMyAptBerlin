from apscheduler.schedulers.blocking import BlockingScheduler
from modules.job import ScrapingJob


def run_scraping_job():
    global last_data

    # job = ScrapingJob('https://immosuche.degewo.de/de/search',
    #                   "article-list__item",
    #                   1,
    #                   "article__title",
    #                   "article__meta",
    #                   "article__tags",
    #                   "article__properties",
    #                   "article__price-tag")

    job = ScrapingJob('https://www.wbm.de/wohnungen-berlin/angebote/',
                      "openimmo-search-list-item",
                      None,
                      "imageTitle",
                      "address",
                      "check-property-list",
                      "main-property-size",
                      "main-property-rent"
                      )
    job.run()

    current_data = job.processor.get_data()
    print(current_data)

    if last_data is not None:
        if not current_data.equals(last_data):
            print("Data has changed!")
            print("Differences:")
            print(current_data.compare(last_data))
        else:
            print("No change in data.")

    last_data = current_data



if __name__ == "__main__":
    run_scraping_job()
#     scheduler = BlockingScheduler()
#     scheduler.add_job(run_scraping_job, 'interval', seconds=30)
#     scheduler.start()
