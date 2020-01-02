import os
import sys

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from common.cloudAMQP_client_mod import CloudAMQPClient
from common import cloudAMQP_client_mod as cc

SCRAPE_NEWS_TASK_QUEUE_URL = cc.CLOUDAMQP_URL
SCRAPE_NEWS_TASK_QUEUE_NAME = "news-manager-scrape-task"

DEDUPE_NEWS_TASK_QUEUE_URL = cc.CLOUDAMQP_URL
DEDUPE_NEWS_TASK_QUEUE_NAME = "news-manager-dedupe-task"

def clearQueue(queue_url, queue_name):
    queue_client = CloudAMQPClient(queue_url, queue_name)

    num_of_messages = 0

    while True:
        if queue_client is not None:
            msg = queue_client.getMessage()
            if msg is None:
                print("Cleared %d messages." % num_of_messages)
                return
            num_of_messages += 1


if __name__ == "__main__":
    clearQueue(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)
    #clearQueue(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
