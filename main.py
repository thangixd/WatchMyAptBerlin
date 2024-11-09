from module.job import ScrapingJob

if __name__ == "__main__":
    base_url = 'https://immosuche.degewo.de/de/search'
    target_class = "article-list__item"
    job = ScrapingJob(base_url, target_class)
    job.run()
    print(job.processor.get_data())
