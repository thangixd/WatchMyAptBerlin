from apscheduler.schedulers.blocking import BlockingScheduler
from module.job import ScrapingJob

last_data = None


def run_scraping_job():
    global last_data

    base_url = 'https://immosuche.degewo.de/de/search'
    target_class = "article-list__item"
    job = ScrapingJob(base_url, target_class)
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

    scheduler = BlockingScheduler()
    scheduler.add_job(run_scraping_job, 'interval', seconds=30)
    scheduler.start()
