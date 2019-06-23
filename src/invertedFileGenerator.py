import io
import json
import sys
from collections import Counter

import jieba

from newsData import *
from stopwords import stopwords

time_range = 'month' # or week
target = 'title' # or content

if __name__ == "__main__":
    filename = sys.argv[1]
    collection = NewsDataCollection(filename)

    invertedDict = dict()

    for newsData in collection.items():
        cntr = Counter()
        if target == 'title':
            words = jieba.cut(newsData.title)
        elif target == 'content':
            words = jieba.cut(newsData.content)
        cntr.update(words)
        for w, cnt in cntr.items():
            if w not in stopwords and not w.isnumeric():
                if w not in invertedDict:
                    invertedDict[w] = {}
                    invertedDict[w]['docs'] = []
                invertedDict[w]['docs'].append({newsData.url: cnt})

    outFilename = '../inverted/' + time_range + '/' + filename.split('/')[-1].split('.')[0] + '_title.json'
    with io.open(outFilename, 'w', encoding='utf8') as f:
        json.dump(invertedDict, f, ensure_ascii=False)
