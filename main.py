from pandas import set_option

import module
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

page = 1
df2 = pd.DataFrame(columns=["Meta", "Title", "Tag", "Properties", "Price-Tag"])

while True:
    url = 'https://immosuche.degewo.de/de/search?page=' + str(page)
    response = urllib.request.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html, 'html.parser')

    target = "article-list__item"

    if soup.find_all(class_=target).__len__() == 0:
        break

    for i, tag in enumerate(soup.find_all(class_=target)):
        meta = tag.find_next(class_="article__meta")
        title = tag.find_next(class_="article__title")
        tags = tag.find_next(class_="article__tags")
        properties = tag.find_next(class_="article__properties")
        price_tag = tag.find_next(class_="article__price-tag")
        df2.loc[i + (page - 1) * 10] = [meta.text, title.text, tags.text if tags else "", properties.text,
                                        price_tag.text]

    page += 1

print(df2)