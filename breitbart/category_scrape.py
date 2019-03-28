import requests
import asyncio
import aiohttp
import os
from bs4 import BeautifulSoup as bsoup
from datetime import datetime, timedelta

NUM_THREADS = 32
START_DATE = datetime(2010, 1, 1) # Jan 1st, 2007
END_DATE = datetime(2019, 1, 1) # Today-ish
BASE_URL = "https://breitbart.com/{category}/{year}/{month}/{day}"

delta = timedelta(1) #move in increments of 1 day
with open('data/categories.txt', 'rt') as f:
    categories = f.read().strip().split()

class AsyncScraper:
    def __init__(self, category):
        self.curr = -1
        self.category = category
        self.curr_date = START_DATE
        self.output_file = './data/articles/{}.txt'.format(category)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    async def scrape_task(self):
        while self.curr_date != END_DATE:
            url = BASE_URL.format(
                category='politics',
                year=self.curr_date.year,
                month=self.curr_date.month,
                day=self.curr_date.day
            )
            print(url)
            self.curr_date += delta
            response = await self.session.get(url)
            text = await response.text()
            self.parse_list_page(text)

    def parse_list_page(self, html):
        soup = bsoup(html, features='html5lib')
        articles = soup.find('section', class_='aList')
        if not articles:
            print(articles)
            return
        with open(self.output_file, 'at') as f:
            for article in articles.findAll('article'):
                link = article.find('a')
                if link:
                    print(link.get('href'))
                    f.write(link.get('href'))
                    f.write('\n')

    async def handler(self):
        async with aiohttp.ClientSession() as self.session:
            tasks = [
                asyncio.ensure_future(self.scrape_task())
                for i in range(NUM_THREADS)
            ]
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED
            )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for category in categories:
        loop.run_until_complete(AsyncScraper(category).handler())