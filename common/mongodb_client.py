from pymongo import MongoClient
MONGO_DB_HOST= 'localhost'
MONGO_DB_PORT=27017
DB_NAME='demo'

client=MongoClient(MONGO_DB_HOST,MONGO_DB_PORT)
# If there is no previously created database with this name, MongoDB will implicitly create one for the user.
def get_db(db=DB_NAME):  # here db is a default argument. if nothing is mentioned while calling the func, demo will be called
    db=client[db]
    return db

