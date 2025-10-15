from motor.motor_asyncio import AsyncIOMotorClient

from src.lib.rok_data import MongoDBClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "rok_prod"

moto_client = AsyncIOMotorClient(MONGO_URI)
async_db = moto_client[DB_NAME]
characters_collection = async_db["characters"]
accounts_collection = async_db["accounts"]
tasks_collection = async_db["tasks"]

sync_db = MongoDBClient(uri=MONGO_URI, db_name=DB_NAME).db
sync_tasks_collection = sync_db["tasks"]
