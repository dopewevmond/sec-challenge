import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class DataWriter:
    def __init__(self):
        mongo_host = os.environ.get("MONGO_DB_HOST", "localhost")
        mongo_username = os.environ.get("MONGODB_USERNAME", "username")
        mongo_password = os.environ.get("MONGO_DB_PASSWORD", "password")
        mongo_database = os.environ.get("MONGODB_DBNAME", "database")
        client = MongoClient(
            mongo_host, 27017, username=mongo_username, password=mongo_password
        )
        self.db = client[mongo_database]

    def save_cve(self, data=None):
        for v in data["vulnerabilities"]:
            self.db["cve"].insert_one(v)

    def save_cve_history(self, data):
        for c in data["cveChanges"]:
            self.db["cve_history"].insert_one(c)
        
