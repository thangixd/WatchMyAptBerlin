import urllib.request
from bs4 import BeautifulSoup
import pandas as pd

class WebScraper:
    def __init__(self, base_url, target_class):
        self.base_url = base_url
        self.target_class = target_class

    def fetch_page(self, page_number):
        url = f'{self.base_url}?page={page_number}'
        response = urllib.request.urlopen(url)
        html = response.read()
        return BeautifulSoup(html, 'html.parser')

    def scrape_page(self, page_number):
        soup = self.fetch_page(page_number)
        if not soup.find_all(class_=self.target_class):
            return None

        articles = []
        for tag in soup.find_all(class_=self.target_class):
            meta = tag.find_next(class_="article__meta")
            title = tag.find_next(class_="article__title")
            tags = tag.find_next(class_="article__tags")
            properties = tag.find_next(class_="article__properties")
            price_tag = tag.find_next(class_="article__price-tag")

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