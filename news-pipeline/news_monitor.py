from common import NewsAPI_Client, cloudAMQP_client_mod as ac
import logging
import redis
import hashlib
import datetime

SCRAPE_NEWS_TASK_QUEUE_URL= ac.CLOUDAMQP_URL
SCRAPE_NEWS_TASK_QUEUE_NAME= "news-manager-scrape-task"
SLEEP_TIME_IN_SECONDS= 30 
NEWS_TIME_OUT_IN_SECONDS=3600 * 24 * 3 # after 3 days, news will be removed from the redis database

logger_format = '%(asctime)s - %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('news_monitor')
logger.setLevel(logging.DEBUG)

# connect redis client and CloudAMQP
REDIS_HOST='localhost'
REDIS_PORT=6379 # By Default, Redis-CLI runs on port 6379.
redis_client=redis.StrictRedis(REDIS_HOST,REDIS_PORT)
cloudAMQP_client = ac.CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)

def run():
    while True:
        news_list= NewsAPI_Client.get_news()
        num_of_new_news=0
        for news in news_list:
            # print(news.keys())
            if news['title'] is None:
                news['title'] = ""
            news_digest= hashlib.md5(news['title'].encode('utf-8')).hexdigest()
             # checks whether any other news has the same title or not
            if redis_client.get(news_digest) is None:
                num_of_new_news=num_of_new_news+1
                # adding a field called digest to store the hash
                news['digest']=news_digest 

            # if published_at is absent then it might cause problems so here we will set the date and time at which it is extracted as published date
            if news['publishedAt'] is None:
                news['publishedAt'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            redis_client.set(news_digest,"True")
            redis_client.expire(news_digest,NEWS_TIME_OUT_IN_SECONDS)
            cloudAMQP_client.sendMessage(news)  # a single article is being transmitted at a time
        print ("monitor found %d new news" % num_of_new_news)
        cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)

if __name__ == "__main__":
    run()





