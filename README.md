python版本为3.12.0

第三方库均在requirements.txt中表明，运行前请自行pip

这个爬虫仅可以用于获取arxiv[https://arxiv.org/]网站的search界面和list界面，输入时请输入正确的url

例：https://arxiv.org/list/astro-ph/new

https://arxiv.org/search/?query=Hawking%2C+Stephen&searchtype=all&source=header

由于这个项目主要是用于研究异步编程，所以爬虫部分很多优化并没有做，比如搜索部分可能会有多页的翻页功能，以及
aiohttp时可能会因不知原因导致的timeout。
