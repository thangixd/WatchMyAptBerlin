import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
from requests.exceptions import ProxyError, SSLError, ConnectTimeout


class WebScraper:
    def __init__(self, base_url, target_class, pager_number=None, title_class=None, meta_class=None,
                 tags_class=None, properties_class=None, price_class=None, proxy=None):
        self.base_url = base_url
        self.target_class = target_class
        self.pager_number = pager_number
        self.title_class = title_class
        self.meta_class = meta_class
        self.tags_class = tags_class
        self.properties_class = properties_class
        self.price_class = price_class
        self.proxy = proxy
        self.session = requests.Session()

    def set_proxy(self, proxy):
        """Set or update proxy configuration.

        Args:
            proxy (dict): Proxy configuration in the format:
                {'http': 'http://user:pass@host:port',
                 'https': 'https://user:pass@host:port'}
        """
        self.proxy = proxy

    def test_proxy(self):
        """Test if the proxy is working."""
        if not self.proxy:
            return False

        try:
            response = self.session.get(
                'https://httpbin.org/ip',
                proxies=self.proxy,
                timeout=10
            )
            return response.status_code == 200
        except (ProxyError, SSLError, ConnectTimeout) as e:
            print(f"Proxy test failed: {str(e)}")
            return False

    def fetch_page(self, page_number=None, max_retries=3):
        """Fetches a page of HTML and returns a BeautifulSoup object.
        Using a UserAgent to simulate a browser and proxy if configured."""

        url = f"{self.base_url}?page={page_number}" if page_number else self.base_url
        print(f"Fetching: {url}")
        user_agent = UserAgent().random
        headers = {'User-Agent': user_agent}

        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=self.proxy,
                    timeout=30
                )
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')

            except ProxyError as e:
                print(f"Proxy error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    print("Max retry attempts reached. Continuing without proxy...")
                    try:
                        response = self.session.get(url, headers=headers, timeout=10)
                        response.raise_for_status()
                        return BeautifulSoup(response.content, 'html.parser')
                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching page without proxy: {str(e)}")
                        return None

            except requests.exceptions.RequestException as e:
                print(f"Error fetching page (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    return None

            import time
            time.sleep(2 ** attempt)

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


class DataProcessor:
    def __init__(self):
        self.df = pd.DataFrame(columns=["Meta", "Title", "Tag", "Properties", "Price-Tag"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

    def add_data(self, articles, start_index=0):
        """Adds scraped articles to the DataFrame."""
        for i, article in enumerate(articles):
            self.df.loc[start_index + i] = article

    def clean_data(self, df):
        # Clean and format 'Price-Tag' column
        df['Price-Tag'] = (
            df['Price-Tag']
            .str.extract(r'([\d\.,]+)')[0]
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
            .apply(lambda x: f"{x:.2f} Euro")
        )

        # Clean and format 'Properties' column
        df['Properties'] = (
            df['Properties']
            .str.extract(r'(\d{1,3}(?:[.,]\d{1,2})?)\s*m²')[0]
            .str.replace(',', '.', regex=True)
            .astype(float)
            .apply(lambda x: f"{x:.2f} m²")
        )

        return df

    def get_data(self):
        return self.df
