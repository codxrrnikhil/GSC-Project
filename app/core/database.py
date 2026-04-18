from pymongo import MongoClient


MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "media_agent"

client = MongoClient(MONGODB_URL)


def get_database():
    return client[DB_NAME]
