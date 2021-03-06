# just copy from the main
#

from common.cloudAMQP_client_mod import CloudAMQPClient
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
from dateutil import parser
from common import news_topic_modelling_service_client, cloudAMQP_client_mod as cc, mongodb_client

DEDUPE_NEWS_TASK_QUEUE_URL = cc.CLOUDAMQP_URL
DEDUPE_NEWS_TASK_QUEUE_NAME = "news-manager-dedupe-task"
SLEEP_TIME_IN_SECONDS = 1


SAME_NEWS_SIMILARITY_THRESHOLD = 0.9

logger_format = '%(asctime)s - %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('news_deduper')
logger.setLevel(logging.DEBUG)


NEWS_TABLE_NAME = "news_col"
cloudAMQP_client = CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)

db= mongodb_client.get_db("demo_news")
# col=db.get_collection("news_col")

cloudAMQP_client = CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)

news = cloudAMQP_client.getMessage()
def handle_message(news):
    text = news['text']
    description = news['description']
    if description is None:
        description = news['title']
    news['publishedAt'] = parser.parse(news['publishedAt'])  # why parser?- allows us to parse most known formats of date-time
    published_at=parser.parse(str(news['publishedAt']))
    published_at_day_begin = datetime.datetime(published_at.year, published_at.month, published_at.day, 0, 0, 0, 0)
    published_at_day_end = published_at_day_begin + datetime.timedelta(days=1)
    same_day_news_list = list(db[NEWS_TABLE_NAME].find({'publishedAt': {'$gte': published_at_day_begin, '$lt': published_at_day_end}}))  # this step remains the problem
    print(same_day_news_list) # list is always empty

    if same_day_news_list is not None and len(same_day_news_list) > 0:
        documents = [news['text'] for news in same_day_news_list]  # this just takes the existing news['text'] into doc
        documents.insert(0, text)  # this adds the text that came from the news in pipeline to the top of the list

        # Calculate similarity matrix
        tfidf = TfidfVectorizer().fit_transform(documents)
        pairwise_sim = tfidf * tfidf.T

        #logger.debug("Pairwise Sim:%s", str(pairwise_sim))

        rows, _ = pairwise_sim.shape  # just putting the first output of the result in rows variable

        for row in range(1, rows):
            if pairwise_sim[row, 0] > SAME_NEWS_SIMILARITY_THRESHOLD:  # why only [row,0]
                # Duplicated news. Ignore.
                logger.info("Duplicated news. Ignore.")
                return





    # if same_day_news_list is not None and len(same_day_news_list) > 0:
    #     documents = [news['text'] for news in same_day_news_list]  # this just takes the existing news['text'] into doc
    #     documents.insert(0, text)  # this adds the text that came from the news in pipeline to the top of the list
    # print("hello2")
    # print(documents)
    # # calculate similarity matrix
    # tfifd=TfidfVectorizer.fit_transform(documents) # it returns a sparse matrix
    # pairwise_sim = tfifd * tfifd.T
    # logger.debug("Pairwise Sim:%s", str(pairwise_sim))
    # rows,_ = pairwise_sim.shape()
    # # print("hello3")
    # for row in range(1,rows):
    #     if pairwise_sim[row, 0] > SAME_NEWS_SIMILARITY_THRESHOLD:  # since pairwise_sim is a matrix, indexes are [row, 0]
    #         # here we only take [row,0] because it conatins values of * of 1st doc with every other doc
    #         # Duplicated news. Ignore.
    #         logger.info("Duplicated news. Ignore.")
    #         return
    # # print("hello3")
    topic = news_topic_modelling_service_client.classify(description)
    news['class'] = topic
    db[NEWS_TABLE_NAME].replace_one({'digest': news['digest']}, news, upsert=True)

print("break3")
def run():
    while True:
        if cloudAMQP_client is not None:
            news = cloudAMQP_client.getMessage()
            if news is not None:
                # Parse and process the task
                try:
                    handle_message(news)
                except Exception as e:
                    print("hello from exception")
                    print(e)


            cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)

if __name__ == "__main__":
    run()