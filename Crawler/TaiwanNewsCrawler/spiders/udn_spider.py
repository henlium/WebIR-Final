"""
聯合報
the crawl deal with udn's news
Usage: scrapy crawl udn -o <filename.json>

Set CRAWLED_DAYS to how many days to be crawled from the start date (included)
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
import scrapy
from conf import *

class UdnSpider(scrapy.Spider):
    name = "udn"

    def start_requests(self):
        url = 'https://udn.com/news/breaknews/1/99'
        meta = {'iter_time': 1}
        yield scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response):
        has_next_page = True
        is_first_iter = response.meta['iter_time'] == 1
        response.meta['iter_time'] += 1
        el_selector = '#breaknews_body dt' if is_first_iter else 'dt'
        target = response.css(el_selector)
        print(len(target))
        if not target:
            has_next_page = False
        for news in target:
            url = news.css('a::attr(href)').extract_first()
            url = response.urljoin(url)
            date_time = news.css('.info .dt::text').extract_first()

            if date_time == None:
                continue
                
            date_time = datetime.strptime(date_time + ' 2019', '%m-%d %H:%M %Y')
            if date_time.date() >= ENDDATE.date():
                continue
            if date_time.date() < STARTDATE.date():
                has_next_page = False
                break

            yield scrapy.Request(url, callback=self.parse_news)

        if has_next_page:
            iter_time = response.meta['iter_time']
            yield scrapy.FormRequest(
                url='https://udn.com/news/get_breaks_article/%d/1/99' %
                iter_time,
                callback=self.parse,
                meta=response.meta)

    def parse_news(self, response):
        title = response.css('h1::text').extract_first()
        date_of_news = response.css(
            '.story_bady_info_author span::text').extract_first()[:10]

        content = ""
        for p in response.css('#story_body_content p::text').extract():
            content += p

        category_links = response.css('div div div.only_web a')
        category = category_links[1].css('::text').extract_first()

        yield {
            'website': "聯合報",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': category
        }
