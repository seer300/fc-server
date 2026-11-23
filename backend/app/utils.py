"""通用工具函数。"""
from bson import ObjectId
from fastapi import HTTPException


def oid(id_str: str) -> ObjectId:
    """字符串转 ObjectId，失败时抛出 400。"""
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail=f"无效的ID: {id_str}")


def serialize(doc):
    """把 MongoDB 文档的 _id 转为 id 字符串，便于前端使用。"""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


def serialize_list(docs):
    return [serialize(d) for d in docs]
