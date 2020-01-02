from common.cloudAMQP_client_mod import CloudAMQPClient
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
from dateutil import parser
from common import news_topic_modelling_service_client, cloudAMQP_client_mod as cc, mongodb_client

DEDUPE_NEWS_TASK_QUEUE_URL = cc.CLOUDAMQP_URL
DEDUPE_NEWS_TASK_QUEUE_NAME = "news-manager-dedupe-task"
SLEEP_TIME_IN_SECONDS = 0.5


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
    print(same_day_news_list) 

    if same_day_news_list is not None and len(same_day_news_list) > 0:
        documents = [news['text'] for news in same_day_news_list]  
        #adds the text that came from the news in pipeline to the top of the list
        documents.insert(0, text)  

        # Calculate similarity matrix
        tfidf = TfidfVectorizer().fit_transform(documents)
        pairwise_sim = tfidf * tfidf.T

        #logger.debug("Pairwise Sim:%s", str(pairwise_sim))

        rows, _ = pairwise_sim.shape  

        for row in range(1, rows):
            if pairwise_sim[row, 0] > SAME_NEWS_SIMILARITY_THRESHOLD:  
                # Duplicated news. Ignore.
                logger.info("Duplicated news. Ignore.")
                return

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
