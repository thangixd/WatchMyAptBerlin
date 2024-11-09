import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent



class WebScraper:
    def __init__(self, base_url, target_class, pager_number=None, title_class=None, meta_class=None, tags_class=None, properties_class=None, price_class=None):
        self.base_url = base_url
        self.target_class = target_class
        self.pager_number = pager_number
        self.title_class = title_class
        self.meta_class = meta_class
        self.tags_class = tags_class
        self.properties_class = properties_class
        self.price_class = price_class


    def fetch_page(self, page_number=None):
        if page_number is None:
            url = self.base_url
        else:
            url = f'{self.base_url}?page={page_number}'

        ua = UserAgent()
        random_ua = ua.random
        print(random_ua)
        request_headers = {
            'user-agent': random_ua
        }


        request = urllib.request.Request(url, headers=request_headers)
        print(request)
        response = urllib.request.urlopen(request)
        html = response.read()
        return BeautifulSoup(html, 'html.parser')

    def scrape_page(self, page_number):
        soup = self.fetch_page(page_number)
        if not soup.find_all(class_=self.target_class):
            return None

        articles = []
        for tag in soup.find_all(class_=self.target_class):
            meta = tag.find_next(class_=self.meta_class)
            title = tag.find_next(class_=self.title_class)
            tags = tag.find_next(class_=self.tags_class)
            properties = tag.find_next(class_=self.properties_class)
            price_tag = tag.find_next(class_=self.price_class)


            article = {
                "Meta": meta.text if meta else "",
                "Title": title.text if title else "",
                "Tag": tags.text if tags else "",
                "Properties": properties.text if properties else "",
                "Price-Tag": price_tag.text if price_tag else ""
            }
            articles.append(article)
        return articles



class DataProcessor:
    def __init__(self):
        self.df = pd.DataFrame(columns=["Meta", "Title", "Tag", "Properties", "Price-Tag"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

    def add_data(self, articles, start_index):
        for i, article in enumerate(articles):
            self.df.loc[start_index + i] = article

    def get_data(self): return self.df