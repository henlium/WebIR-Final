"""
聯合報
the crawl deal with udn's news
Usage: scrapy crawl udn -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
import scrapy

CRAWLED_DAYS = 2
DAYS_STR = []
for i in range(CRAWLED_DAYS):
    day_str = (datetime.now() - timedelta(i)).strftime('%m-%d')
    DAYS_STR.append(day_str)

class UdnSpider(scrapy.Spider):
    name = "udn"

    def start_requests(self):
        print(DAYS_STR)
        url = 'https://udn.com/news/breaknews/1/99#breaknews'
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
            date_in_range = False
            for day_str in DAYS_STR:
                if day_str in date_time:
                    date_in_range = True
                    break
            if not date_in_range:
                print('break here ' + date_time)
                has_next_page = False
                break

            yield scrapy.Request(url, callback=self.parse_news)

        if has_next_page:
            iter_time = response.meta['iter_time']
            yield scrapy.FormRequest(
                url='https://udn.com/news/get_breaks_article/%d/1/0' %
                iter_time,
                callback=self.parse,
                meta=response.meta)

    def parse_news(self, response):
        title = response.css('h1::text').extract_first()
        date_of_news = response.css(
            '.story_bady_info_author span::text').extract_first()[:10]

        content = ""
        for p in response.css('p'):
            p_text = p.css('::text')
            if p_text:
                content += ' '.join(p_text.extract())

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
