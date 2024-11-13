from modules.scraper import WebScraper, DataProcessor

class BaseScrapingJob:
    def __init__(self, base_url, target_class, page_number, title_class, meta_class, tags_class, properties_class, price_class):
        self.scraper = WebScraper(base_url, target_class, page_number, title_class, meta_class, tags_class, properties_class, price_class)
        self.processor = DataProcessor()
        self.page = page_number

    def add_scraped_data(self, articles, offset_multiplier):
        """Helper function to add scraped data with an offset."""
        if articles:
            self.processor.add_data(articles, (self.page - 1) * offset_multiplier)

class WBMScrapingJob(BaseScrapingJob):
    def __init__(self, base_url, target_class, page_number, title_class, meta_class, tags_class, properties_class, price_class):
        super().__init__(base_url, target_class, page_number, title_class, meta_class, tags_class, properties_class, price_class)

    def run(self):
        articles = self.scraper.scrape_page(self.page)
        self.page = 1
        self.add_scraped_data(articles, 10)
        self.page += 1

class DegewoScrapingJob(BaseScrapingJob):
    def __init__(self, base_url, target_class, page_number, title_class, meta_class, tags_class, properties_class, price_class):
        super().__init__(base_url, target_class, page_number, title_class, meta_class, tags_class, properties_class, price_class)

    def run(self):
        while True:
            articles = self.scraper.scrape_page(self.page)
            if articles is None:
                break
            self.add_scraped_data(articles, 10)
            self.page += 1
