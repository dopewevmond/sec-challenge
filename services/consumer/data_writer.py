import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class DataWriter:
    def __init__(self):
        mongo_host = 'mongodb'
        mongo_username = os.environ.get("MONGODB_USERNAME", "mongouser")
        mongo_password = os.environ.get("MONGO_DB_PASSWORD", "password")
        mongo_database = os.environ.get("MONGODB_DBNAME", "mongodb")
        client = MongoClient(
            mongo_host, 27017, username=mongo_username, password=mongo_password
        )
        self.db = client[mongo_database]

    def save_cve(self, data=None):
        for v in data["vulnerabilities"]:
            v["timestamp"] = datetime.now()
            self.db["cve"].insert_one(v)

    def save_cve_history(self, data):
        for c in data["cveChanges"]:
            c["timestamp"] = datetime.now()
            self.db["cve_history"].insert_one(c)

    def fetch_cve_records(self, offset=0, limit=10):
        total_records = self.db["cve"].count_documents({})
        cve_cursor = (
            self.db["cve"].find({}).skip(offset).limit(limit).sort("timestamp", -1)
        )
        cve_records = []

        for record in cve_cursor:
            record["_id"] = str(record["_id"])
            record["timestamp"] = str(record["timestamp"])
            cve_records.append(record)
        return {"total_records": total_records, "cve_records": list(cve_records)}
