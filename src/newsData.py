import json
from datetime import datetime

def as_newsData(dct):
    return NewsData(dct['url'], dct['title'], dct['date'], dct['content'], dct['category'])

class NewsData:
    """ Contains data of news

    Attributes
    ----------
        url : str
        title : str
        date : datetime
        content : str
        category : str
    """
    def __init__(self, url, title, _date, content, category):
        self.url = url
        self.title = title
        self.date = datetime.strptime(_date, '%Y-%m-%d')
        self.content = content
        self.category = category

class NewsDataCollection:
    """ A collection of NewsData

    Attributes
    ----------
        website : str
            Representing the source of this collection. Written in chinese

    Methods
    -------
        NewsDataCollection(filename)
            Constructor
            Read the json file specified by `filename` and parse the data insides.
        items()
            A helper method for iteration.
        getByUrl(url)
            Return NewsData specified by `url`
    """
    
    def __init__(self, filename):
        self.readfile(filename)

    def readfile(self, filename):
        f = open(filename, 'r', encoding='utf-8')
        self.newsList = json.load(f, object_hook=as_newsData)
        f.close()
        f = open(filename, 'r', encoding='utf-8')
        self.website = json.load(f)[0]['website']
        self.urlDict = dict()
        for i in self.newsList:
            self.urlDict[i.url] = i

    def items(self):
        """For iteration

        A helper method for iteration. Do not modify anything in the return value
        
        Returns:
            A list of `NewsData`
        """
        return self.newsList
    
    def hasUrl(self, url):
        if url in self.urlDict:
            return True
        return False

    def getByUrl(self, url):
        """Get a `NewsData` by URL
        
        Parameters
        ----------
            url : str
                Requested URL
        
        Returns
        -------
            NewsData
                return None if url is invalid
        """
        if url in self.urlDict:
            return self.urlDict[url]
        return None
    