"""MongoDB 连接管理（单例）。"""
from pymongo import MongoClient

from .config import MONGO_URI, MONGO_DB

_client: MongoClient | None = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI)
        _db = _client[MONGO_DB]
    return _db


def get_collection(name: str):
    return get_db()[name]
