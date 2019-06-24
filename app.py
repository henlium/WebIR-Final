import json
import os
import urllib.parse
from collections import Counter
from math import log, exp
from datetime import timedelta

import jieba
import requests
from flask import (Flask, make_response, redirect, render_template,
                   request, send_from_directory)

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

app = Flask(__name__)

def getNews(query_news, website):
    # counting query term frequency
    content_cnt = Counter()
    query_words = list(jieba.cut(query_news.content))
    content_cnt.update(query_words)
    title_cnt = Counter()
    query_words = list(jieba.cut(query_news.content))
    title_cnt.update(query_words)

    retList = []
    for j in range(len(collections)):
        col = collections[j]
        if col.website == website:
            continue
        # calculate scores by tf-idf
        news_scores = dict() # record candidate document and its scores
        invert_file = inverted_files[j]
        for word, count in content_cnt.items():
            if word in invert_file:
                query_tf = count
                qtf = ((k3+1) * query_tf) / (k3 + query_tf)
                # idf = invert_file[word]['idf']
                df = len(invert_file[word]['docs'])
                try:
                    idf = log((len(col.items()) - df + 0.5) / (df + 0.5))
                except ValueError:
                    print(col.website, word, df, len(col.items()))
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
                idf = log((len(col.items()) - df + 0.5) / (df + 0.5))
                for url_count_dict in invert_file[word]['docs']:
                    for url, doc_tf in url_count_dict.items():
                        tf = 1 + log(doc_tf)
                        if url in news_scores:
                            news_scores[url] += query_tf * idf * tf
                        else:
                            news_scores[url] = query_tf * idf * tf
        for url, score in news_scores.items():
            days = (query_news.date - col.getByUrl(url).date).days
            days = abs(days)
            news_scores[url] = score / exp(days / 4.)

        # sort the document score pair by the score
        sorted_document_scores = sorted(news_scores.items(), key=lambda kv: kv[1], reverse=True)
        targetUrl = sorted_document_scores[0][0]
        retList.append([col.website, targetUrl, col.getByUrl(targetUrl).title])
    return retList

@app.route('/seemore')
def retrieve():
    url = request.args.get('url')
    url = urllib.parse.unquote(url)
    for col in collections:
        if col.hasUrl(url):
            news = col.getByUrl(url)
            ret = getNews(news, col.website)
            return json.dumps(ret).encode('utf8')
    print('not in database')
    return 'QAQ'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
