"""
the crawl deal with ettoday's news
Usage: scrapy crawl ettoday -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import sys
import traceback
from datetime import datetime, timedelta
from conf import *

# CURDATE = STARTDATE
ROOT_URL = 'https://www.ettoday.net'


class EttodaySpider(scrapy.Spider):
    name = "ettoday"

    def start_requests(self):
        for date in daterange(STARTDATE, ENDDATE):
            url = 'https://www.ettoday.net/news/news-list-' + date.strftime('%Y-%m-%d') + '-0.htm'
            meta = {'iter_time': 0, 'date': date.strftime('%Y/%m/%d')}
            yield scrapy.Request(url, callback=self.parse_news_list, meta=meta)

    def parse_news_list(self, response):
        has_next_page = True
        response.meta['iter_time'] += 1
        is_first_iter = response.meta['iter_time'] == 1
        prefix = '.part_list_2' if is_first_iter else ''
        for news_item in response.css(prefix + ' h3'):
            date = news_item.css('.date ::text').get()[:10]
            if date != response.meta['date']:
                has_next_page = False
                break
            url = news_item.css('a::attr(href)').extract_first()
            url = ROOT_URL + url
            category = news_item.css('em::text').extract_first()
            date_time = news_item.css('span::text').extract_first()

            # if TODAY not in date_time:
            #     has_next_page = False
            #     continue

            response.meta['category'] = category
            yield scrapy.Request(
                url, callback=self.parse_news, meta=response.meta)
        if has_next_page:
            tFile = datetime.strptime(response.meta['date'], '%Y/%m/%d').strftime('%Y%m%d') + '.xml'
            yield scrapy.FormRequest(
                url="https://www.ettoday.net/show_roll.php",
                callback=self.parse_news_list,
                meta=response.meta,
                formdata={
                    'offset': str(response.meta['iter_time']),
                    'tPage': '3',
                    'tFile': tFile,
                    'tOt': '0',
                    'tSi': '100'
                })


    def parse_news(self, response):
        title = response.css('h1.title::text').extract_first()
        if not title:
            title = response.css('h2.title::text').extract_first()
        if not title:
            title = response.css('h1.title_article::text').extract_first()
        if not title:
            title = response.css('.subject_article h1::text').extract_first()

        p_list = response.css('.story p::text').extract()

        date = response.css('.date ::attr(datetime)').get()
        if date == None:
            date = response.css('.news-time ::attr(datetime)').get()
        date = date[:10]

        content = ''
        for p in p_list:
            content += p

        yield {
            'website': "東森新聞雲",
            'url': response.url,
            'title': title,
            'date': date,
            'content': content,
            'category': response.meta['category']
        }
