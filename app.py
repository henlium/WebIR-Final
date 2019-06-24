import json
import os
import urllib.parse
from datetime import timedelta
from math import exp, log

import jieba
import requests
from flask import (Flask, make_response, redirect, render_template, request,
                   send_from_directory)

from src.newsData import *
from retrieve_Okapi import getNews

app = Flask(__name__)

@app.route('/seemore')
def retrieve():
    url = request.args.get('url')
    url = urllib.parse.unquote(url)
    ret = getNews(url)
    if not ret:
        qq = ['QAQ']
        return json.dumps(qq)
    return json.dumps(ret).encode('utf8')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
