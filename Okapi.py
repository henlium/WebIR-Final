#!/usr/bin/env python
# coding: utf-8

import csv
import io
import json
import os
import operator
import random
import traceback
from argparse import ArgumentParser
from collections import Counter
from math import log
from datetime import datetime

import jieba
import numpy as np
import pandas as pd

from src.newsData import *

file_list = [
    'cts.json',
    'ettoday.json',
    'ltn.json',
    'udn.json'
]
file_title_list = [
    'cts_title.json',
    'ettoday_title.json',
    'ltn_title.json',
    'udn_title.json'
]


time_range = 'week'
if time_range == 'week':
    raw_data_dir = 'raw_data/week'
    invert_file_dir = 'inverted/week'
elif time_range == 'month':
    raw_data_dir = 'raw_data/week'
    invert_file_dir = 'inverted/week'

# read query and news corpus
print('Reading files')
collections = []
for fname in file_list:
    collections.append(NewsDataCollection(os.path.join(raw_data_dir, fname)))

# load inverted file
inverted_files = []
for fname in file_list:
    with open(os.path.join(invert_file_dir, fname)) as f:
        inverted_files.append(json.load(f))

inverted_title_files = []
for fname in file_title_list:
    with open(os.path.join(invert_file_dir, fname)) as f:
        inverted_title_files.append(json.load(f))
for i in range(len(inverted_files)):
    invfile = inverted_title_files[i]
    todel = []
    for url, foo in invfile.items():
        if url not in inverted_files[i]:
            todel.append(url)
    for url in todel:
        del(invfile[url])

print('Counting documents length')
doclen = {}
for invfile in inverted_files:
    for term, info in invfile.items():
        for tfdict in info['docs']:
            for url, freq in tfdict.items():
                if url in doclen:
                    doclen[url] += freq
                else:
                    doclen[url] = freq

avdl = sum(v for v in doclen.values()) / len(doclen)

k1 = 2.
b = 0.75
k3 = 500

# random select news as query
queries_list = []
for news_collection in collections:
    tmp = []
    length = len(news_collection.items())
    for i in range(5):
        index = random.randrange(length)
        tmp.append(news_collection.items()[index])
    queries_list.append(tmp)

# process each query
print('Retrieving')
final_ans = []
for i in range(len(collections)):
    queries = queries_list[i]
    media = collections[i].website
    for query_news in queries:
        print(f'website: {media}')
        print(f"query news: {query_news.title}\t{query_news.date}")
        print(f'content: {query_news.content}')

        # counting query term frequency
        content_cnt = Counter()
        query_words = list(jieba.cut(query_news.content))
        content_cnt.update(query_words)
        title_cnt = Counter()
        query_words = list(jieba.cut(query_news.content))
        title_cnt.update(query_words)

        for j in range(len(collections)):
            if i == j:
                continue
            # calculate scores by tf-idf
            news_scores = dict() # record candidate document and its scores
            invert_file = inverted_files[j]
            print(f'website: {collections[j].website}')
            for word, count in content_cnt.items():
                if word in invert_file:
                    query_tf = count
                    qtf = ((k3+1) * query_tf) / (k3 + query_tf)
                    # idf = invert_file[word]['idf']
                    df = len(invert_file[word]['docs'])
                    idf = log((len(collections[j].items()) - df + 0.5) / (df + 0.5))
                    for url_count_dict in invert_file[word]['docs']:
                        for url, doc_tf in url_count_dict.items():
                            tf = ((k1 + 1) * doc_tf) / ((k1 * (1 - b + b * (doclen[url] / avdl))) + doc_tf)
                            if url in news_scores:
                                news_scores[url] += query_tf * idf * tf
                            else:
                                news_scores[url] = query_tf * idf * tf
            # calculate title score
            invert_file = inverted_title_files[j]
            for word, count in title_cnt.items():
                if word in invert_file:
                    query_tf = count
                    qtf = ((k3+1) * query_tf) / (k3 + query_tf)
                    # idf = invert_file[word]['idf']
                    df = len(invert_file[word]['docs'])
                    idf = log((len(collections[j].items()) - df + 0.5) / (df + 0.5))
                    for url_count_dict in invert_file[word]['docs']:
                        for url, doc_tf in url_count_dict.items():
                            tf = 1 + log(doc_tf)
                            if url in news_scores:
                                news_scores[url] += query_tf * idf * tf
                            else:
                                news_scores[url] = query_tf * idf * tf

            # sort the document score pair by the score
            sorted_document_scores = sorted(news_scores.items(), key=lambda kv: kv[1], reverse=True)
            for i in range(5):
                news = collections[j].getByUrl(sorted_document_scores[i][0])
                date = news.date.strftime('%Y/%m/%d')
                print(f'#{i+1} news: {news.title}\t{date}')
                print(f'{news.content}')
                print(f'score: {sorted_document_scores[i][1]}')
                x = input('Continue? Y/n\n')
                x = x.lower()
                while (x != '' and x != 'y' and x != 'n'):
                    x = input('Continue? Y/n\n')
                if x == 'n':
                    break
