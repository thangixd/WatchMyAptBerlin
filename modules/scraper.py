import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent


class WebScraper:
    def __init__(self, base_url, target_class, pager_number=None, title_class=None, meta_class=None, tags_class=None,
                 properties_class=None, price_class=None):
        self.base_url = base_url
        self.target_class = target_class
        self.pager_number = pager_number
        self.title_class = title_class
        self.meta_class = meta_class
        self.tags_class = tags_class
        self.properties_class = properties_class
        self.price_class = price_class

    def fetch_page(self, page_number=None):
        """Fetches a page of HTML and returns a BeautifulSoup object.
        Using a UserAgent to simulate a browser."""

        url = f"{self.base_url}?page={page_number}" if page_number else self.base_url
        print(f"Fetching: {url}")
        user_agent = UserAgent().random
        headers = {'User-Agent': user_agent}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check if request was successful
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

        return BeautifulSoup(response.content, 'html.parser')

    def scrape_page(self, page_number):
        soup = self.fetch_page(page_number)
        if soup is None:
            return None

        elements = soup.find_all(class_=self.target_class)

        print(f"Found {len(elements)} elements on page {page_number}.")

        if not elements:
            return None

        articles = []
        for element in elements:
            article = {
                "Meta": element.find_next(class_=self.meta_class).get_text(strip=True) if element.find_next(
                    class_=self.meta_class) else "",
                "Title": element.find_next(class_=self.title_class).get_text(strip=True) if element.find_next(
                    class_=self.title_class) else "",
                "Tag": element.find_next(class_=self.tags_class).get_text(strip=True) if element.find_next(
                    class_=self.tags_class) else "",
                "Properties": element.find_next(class_=self.properties_class).get_text(strip=True) if element.find_next(
                    class_=self.properties_class) else "",
                "Price-Tag": element.find_next(class_=self.price_class).get_text(strip=True) if element.find_next(
                    class_=self.price_class) else ""
            }
            articles.append(article)

        return articles


def configure_display_options():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)


class DataProcessor:
    def __init__(self):
        self.df = pd.DataFrame(columns=["Meta", "Title", "Tag", "Properties", "Price-Tag"])
        configure_display_options()

    def add_data(self, articles, start_index=0):
        """Adds scraped articles to the DataFrame."""
        for i, article in enumerate(articles):
            self.df.loc[start_index + i] = article

    def get_data(self):
        return self.df