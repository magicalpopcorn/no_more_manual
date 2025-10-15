from dataclasses import dataclass
from typing import List

from pymongo import MongoClient
from pymongo.collection import Collection

try:
    from src.lib import logger
except:
    import logging as logger


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# ==============================================================
#  Dataclasses (models)
# ==============================================================


@dataclass
class Character:
    _id: str
    name: str
    slot_number: int
    ch: int = 25
    rss_order: str = "V1"
    rss_level: int = 8


@dataclass
class Account:
    _id: str
    name: str
    characters: List[str]


# ==============================================================
#  MongoDB Client (singleton)
# ==============================================================


class MongoDBClient(metaclass=SingletonMeta):
    def __init__(self, uri: str = "mongodb://localhost:27017/", db_name: str = "rok_prod"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        logger.debug(f"Connected to MongoDB [{db_name}]")


# ==============================================================
#  Collections DB (singleton)
# ==============================================================


class CharactersDB(metaclass=SingletonMeta):
    def __init__(self):
        self.db: Collection = MongoDBClient().db["characters"]

    def get_by_name(self, name: str) -> Character:
        doc = self.db.find_one({"name": name})
        if not doc:
            raise RuntimeError(f"Character with name '{name}' not found")
        return Character(**doc)

    def get_by_id(self, char_id: str) -> Character:
        doc = self.db.find_one({"_id": char_id})
        if not doc:
            raise RuntimeError(f"Character with ID '{char_id}' not found")
        return Character(**doc)

    def get_all(self) -> List[Character]:
        docs = self.db.find()
        return [Character(**doc) for doc in docs]


class AccountsDB(metaclass=SingletonMeta):
    def __init__(self):
        self.db: Collection = MongoDBClient().db["accounts"]

    def get_by_id(self, account_id: str) -> Account:
        doc = self.db.find_one({"_id": account_id})
        if not doc:
            raise RuntimeError(f"Account with ID '{account_id}' not found")
        return Account(**doc)

    def get_all(self) -> List[Account]:
        docs = self.db.find()
        return [Account(**doc) for doc in docs]


class RssOrdersDB(metaclass=SingletonMeta):
    def __init__(self):
        self.db: Collection = MongoDBClient().db["rss_orders"]

    def get_by_id(self, rss_order_id: str) -> List[str]:
        doc = self.db.find_one({"_id": rss_order_id})
        if not doc:
            raise RuntimeError(f"RssOrder with ID '{rss_order_id}' not found")
        return doc["resources"]
