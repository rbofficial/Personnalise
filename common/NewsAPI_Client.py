import json
from newsapi.newsapi_client import NewsApiClient
newsapi = NewsApiClient(api_key='XXXXX')
NEWS_SOURCES = [
    'bbc-news',
    'bbc-sport',
    'bloomberg',
    'cnn',
    'entertainment-weekly',
    'espn',
    'ign',
    'techcrunch',
    'the-new-york-times',
    'the-wall-street-journal',
    'the-washington-post'
]
news=[]
def get_news():
    for source in NEWS_SOURCES:
        articles_all = newsapi.get_everything(sources=source, language='en')  
        # sort by default is publihed_at
        #popularity might not give us new articles every time we implement this fn
        news.extend(articles_all['articles'])
    return news
