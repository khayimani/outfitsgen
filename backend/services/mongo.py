import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoService:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("MONGO_DB_NAME", "wardrobe_db")
        
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Check connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db["items"]
            print("Connected to MongoDB")
        except ConnectionFailure:
            print("Could not connect to MongoDB (expected if mock/local without DB)")
            self.client = None
            self.db = None
            self.collection = None

    def insert_item(self, item_data):
        if self.collection is None:
            print(f"Mock insert: {item_data}")
            return "mock_id"
        try:
            result = self.collection.insert_one(item_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting into Mongo: {e}")
            return None

    def get_item(self, item_id):
        if self.collection is None:
            return None
        try:
            return self.collection.find_one({"_id": item_id})
        except Exception as e:
            print(f"Error fetching from Mongo: {e}")
            return None

mongo_service = MongoService()
