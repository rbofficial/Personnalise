from common import news_topic_modelling_service_client, mongodb_client

if __name__ == '__main__':
    db = mongodb_client.get_db("demo_news")
    cursor = db['news_col'].find({})
    count = 0
    for news in cursor:
        count += 1
        print(count)
        if 'class' in news: # because i dont have any class column in news db
            print('Populating classes...')
            description = news['description']
            if description is None:
                description = news['title']
            topic = news_topic_modelling_service_client.classify(description)
            news['class'] = topic
            db['news'].replace_one({'digest': news['digest']}, news, upsert=True)
