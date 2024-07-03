import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


class Database:
    def __init__(self) -> None:
        load_dotenv()

        MONGO_URL = os.getenv("MONGO_URL")
        self.client = AsyncIOMotorClient(MONGO_URL)
        self._instance = None

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def get_collection(self, collection_name, database_name="dafarmz"):
        db = self.client.get_database(database_name)

        return db.get_collection(collection_name)
