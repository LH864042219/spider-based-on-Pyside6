from bs4 import BeautifulSoup
import asyncio
from aiohttp_retry import RetryClient, ExponentialRetry
import logging


async def fetch_html(url):
    retry_options = ExponentialRetry(attempts=5, max_timeout=5)
    async with RetryClient(retry_options=retry_options) as client:
        async with client.get(url) as response:
            return await response.content.read()

    # async with aiohttp.ClientSession() as client:
    #     async with client.get(url) as response:
    #         return await response.text()

async def abs_html(url):
    html = await fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    baseurl = "https://arxiv.org"

    content_left = soup.find('div', class_='leftcolumn')
    date = content_left.find('div', class_='dateline').text.strip()
    # date = datetime.strptime(date, '[Submitted on %d %b %Y]').strftime('%Y-%m-%d')
    title = content_left.find('h1', class_='title mathjax').text.split("Title:")[1]
    authors = content_left.find('div', class_='authors').text.split("Authors:")[1]
    subjects = content_left.find('td', class_='tablecell subjects').text.strip()

    download_url = {}
    content_extra = soup.find('div', class_='full-text')
    for li in content_extra.find_all('li'):
        if not 'Other' in li.a.text:
            download_url[li.a.text] = baseurl + li.a['href']
    
    data = {
        'authors' : authors,
        'date' : date,
        'title' : title,
        'subjects' : subjects,
        'download_url' : download_url
    }
    return data

async def get_abs_url(url):
    search_start = "https://arxiv.org/search/"
    list_start = "https://arxiv.org/list/"
    html = await fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    data = []
    if search_start in url:
        content = soup.find('ol', class_='breathe-horizontal')
        for li in content.find_all('li'):
            data.append(li.find('p', class_='list-title is-inline-block').a['href'])

    elif list_start in url:
        baseurl = "https://arxiv.org"
        content = soup.find_all('a', title='Abstract')
        for a in content:
            data.append(baseurl + a['href'])
    return data

if __name__ == "__main__":
    baseurl = "https://arxiv.org/search/?query=Hawking%2C+Stephen&searchtype=all&abstracts=show&order=-announced_date_first&size=50&start=50"
    url = baseurl
    loop = asyncio.get_event_loop()
    datas = loop.run_until_complete(get_abs_url(url))
    total = len(datas)
    for idx, data in enumerate(datas):
        logging.info(f"Processing {data} ({(idx + 1) / total * 100:.2f}%)")
        with open("data.txt", "a") as f:  # Changed "w" to "a" to append to the file
            f.write(str(loop.run_until_complete(abs_html(data))) + "\n")
            f.write("\n")