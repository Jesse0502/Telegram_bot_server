import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def get_database():

    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    CONNECTION_STRING = f"mongodb+srv://{username}:{password}@cluster0.oaste.mongodb.net/TelegramBot?retryWrites=true&w=majority"

    client = MongoClient(CONNECTION_STRING)
    print("Connecting with MongoDb")
    return client["TelegramBot"]


# if __name__ == "__main__":
db = get_database()
