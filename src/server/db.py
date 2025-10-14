from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "rok_prod"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
characters_collection = db["characters"]
accounts_collection = db["accounts"]
