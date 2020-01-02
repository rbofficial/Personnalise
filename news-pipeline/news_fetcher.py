import logging
from newspaper import Article
from common import cloudAMQP_client_mod as cc
from common.cloudAMQP_client_mod import CloudAMQPClient
from dateutil import parser
logger_format = '%(asctime)s - %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('news_fetcher')
logger.setLevel(logging.DEBUG)

SCRAPE_NEWS_TASK_QUEUE_URL=cc.CLOUDAMQP_URL
SCRAPE_NEWS_TASK_QUEUE_NAME="news-manager-scrape-task"
scrape_news_queue_client=CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL,SCRAPE_NEWS_TASK_QUEUE_NAME)

DEDUPE_NEWS_TASK_QUEUE_URL=cc.CLOUDAMQP_URL
DEDUPE_NEWS_TASK_QUEUE_NAME="news-manager-dedupe-task"
dedupe_news_queue_client=CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL,DEDUPE_NEWS_TASK_QUEUE_NAME)
SLEEP_TIME_IN_SECONDS= 1 # this is less than news monitor why?

def handle_news(news1):
    if news1 is None or not isinstance(news1, dict):  # if the news obtained is not in the form of dict, then raise warning
        logger.warning('news is broken')
        return
    news=news1
    news['publishedAt'] = parser.parse(news['publishedAt'])
    # print(news['publishedAt'])
    # print(news['url'])
    article= Article(news1['url'])
    article.download()
    article.parse()
    # print(article.text)
    news['text']= article.text
    dedupe_news_queue_client.sendMessage(news)


def run():
    while True:
        if scrape_news_queue_client is not None:
            news=scrape_news_queue_client.getMessage()
            if news is not None:
                try:
                    # print("hello in try")
                    handle_news(news)
                except Exception as e:
                    # print("hello")
                    logger.warning(e)
                    pass # this means that this block is unimplemented
            scrape_news_queue_client.sleep(SLEEP_TIME_IN_SECONDS)


if __name__ == "__main__":
    run()