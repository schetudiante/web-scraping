import aiohttp
import requests
import os
import json
import asyncio
import time

with open('api_key.txt', 'rt') as f:
    api_keys = f.read().splitlines()

OUTPUT_DIR = os.path.join('.', 'api_data')
API_BASE = ("https://api.nytimes.com/svc/search/v2/articlesearch.json"
            "?sort=oldest"
            "&fl=web_url,byline,type_of_material,headline,pub_date"
            "&page={page}"
            "&api-key={key}")
NUM_TASKS = 1

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
    with open(
        os.path.join(OUTPUT_DIR, '.gitignore'),
        'wt'
    ) as f:
        f.write('\n'.join('*', '-.gitignore'))

completed = {
    int(f[:-5]) for f in os.listdir(OUTPUT_DIR)
    if f.endswith('.json')
}
curr = 0

def get_num_pages():
    url = API_BASE.format(key=api_keys[0], page=0)
    while True:
        response = requests.get(url).json()
        if 'fault' in response:
            continue
        return response['response']['meta']['hits']

def get_page(page):
    url = API_BASE.format(
        key=api_keys[page % len(api_keys)],
        page=page
    )
    print(url)
    r = requests.get(url)
    data = r.json()
    if 'fault' in data:
        return False
    with open(
        os.path.join(OUTPUT_DIR, '{}.json'.format(page)),
        'wt'
    ) as f:
        f.write(json.dumps(data))
    return True 

class AsyncScraper:
    def __init__(self):
        self.curr = -1
        self.completed = completed
        self.num_pages = get_num_pages()


    async def scrape_task(self):
        while self.curr < self.num_pages // 10:
            self.curr += 1
            if self.curr not in self.completed:
                self.completed.add(
                    await self.get_page(self.curr)
                )
                await asyncio.sleep(4)


    async def get_page(self, page):
        url = API_BASE.format(
            key=api_keys[page % len(api_keys)],
            page=page
        )
        print('Starting {}'.format(page))
        for attempt in range(3):
            async with self.session.get(url) as r:
                data = await r.json()
                if 'fault' in data:
                    print('Fault {}'.format(page))
                    await asyncio.sleep(5)
                    continue
                print('Saving data for {}'.format(page))
                with open(
                    os.path.join(OUTPUT_DIR, '{}.json'.format(page)),
                    'wt'
                ) as f:
                    f.write(json.dumps(data, indent=4))
                return page
        return page

    async def handler(self):
        async with aiohttp.ClientSession() as self.session:
            tasks = [
                asyncio.ensure_future(self.scrape_task())
                for i in range(NUM_TASKS)
            ]
            done, pending = await asyncio.wait(
                tasks, 
                return_when=asyncio.FIRST_COMPLETED
            )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncScraper().handler())