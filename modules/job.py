from modules.scraper import WebScraper, DataProcessor

class ScrapingJob:
    def __init__(self, base_url, target_class, page_number, title_class, meta_class, tags_class, properties_class, price_class):
        self.scraper = WebScraper(base_url, target_class, page_number, title_class, meta_class, tags_class, properties_class, price_class)
        self.processor = DataProcessor()
        self.page = page_number

    def run(self):
        while True:
            articles = self.scraper.scrape_page(self.page)
            if articles is None:
                break
            self.processor.add_data(articles, (self.page - 1) * 10)
            self.page += 1

