"""评分问题维护：类别与问题的 CRUD。"""
from fastapi import APIRouter, HTTPException

from ..database import get_collection
from ..utils import oid, serialize, serialize_list

router = APIRouter()
CAT_COLLECTION = "score_category"
Q_COLLECTION = "score_question"


# ---------- 类别 ----------
@router.get("/categories")
def list_categories():
    items = get_collection(CAT_COLLECTION).find({"active": {"$ne": False}}).sort("sort", 1)
    return serialize_list(list(items))


@router.post("/categories")
def create_category(data: dict):
    data.setdefault("weight", 1.0)
    data.setdefault("sort", 0)
    data.setdefault("active", True)
    result = get_collection(CAT_COLLECTION).insert_one(data)
    return {"id": str(result.inserted_id)}


@router.put("/categories/{cat_id}")
def update_category(cat_id: str, data: dict):
    data.pop("_id", None)
    data.pop("id", None)
    result = get_collection(CAT_COLLECTION).update_one(
        {"_id": oid(cat_id)}, {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "类别不存在")
    return {"updated": True}


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: str):
    get_collection(CAT_COLLECTION).update_one({"_id": oid(cat_id)}, {"$set": {"active": False}})
    get_collection(Q_COLLECTION).update_many(
        {"category_id": cat_id}, {"$set": {"active": False}}
    )
    return {"deleted": True}


# ---------- 问题 ----------
@router.get("")
def list_questions(category_id: str | None = None):
    query = {"active": {"$ne": False}}
    if category_id:
        query["category_id"] = category_id
    items = get_collection(Q_COLLECTION).find(query).sort("sort", 1)
    return serialize_list(list(items))


@router.post("")
def create_question(data: dict):
    data.setdefault("question_type", "single")
    data.setdefault("sort", 0)
    data.setdefault("active", True)
    result = get_collection(Q_COLLECTION).insert_one(data)
    return {"id": str(result.inserted_id)}


@router.put("/{question_id}")
def update_question(question_id: str, data: dict):
    data.pop("_id", None)
    data.pop("id", None)
    result = get_collection(Q_COLLECTION).update_one(
        {"_id": oid(question_id)}, {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "问题不存在")
    return {"updated": True}


@router.delete("/{question_id}")
def delete_question(question_id: str):
    get_collection(Q_COLLECTION).update_one(
        {"_id": oid(question_id)}, {"$set": {"active": False}}
    )
    return {"deleted": True}
