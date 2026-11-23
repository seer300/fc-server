"""问答模块：分类 / 问题 / 答案记录（独立于评分模块，答案不参与计分）。"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from ..database import get_collection
from ..utils import oid, serialize, serialize_list

router = APIRouter()
CAT_COLLECTION = "qa_category"
Q_COLLECTION = "qa_question"
A_COLLECTION = "qa_answer"


def _now():
    return datetime.now(timezone.utc)


# ---------- 分类 ----------
@router.get("/categories")
def list_categories(target_type: str = Query("community")):
    items = get_collection(CAT_COLLECTION).find(
        {"target_type": target_type, "active": {"$ne": False}}
    ).sort("sort", 1)
    return serialize_list(list(items))


@router.post("/categories")
def create_category(data: dict):
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
        raise HTTPException(404, "分类不存在")
    return {"updated": True}


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: str):
    get_collection(CAT_COLLECTION).update_one(
        {"_id": oid(cat_id)}, {"$set": {"active": False}}
    )
    get_collection(Q_COLLECTION).update_many(
        {"category_id": cat_id}, {"$set": {"active": False}}
    )
    return {"deleted": True}


# ---------- 问题 ----------
@router.get("/questions")
def list_questions(target_type: str | None = None, category_id: str | None = None):
    query = {"active": {"$ne": False}}
    if target_type:
        query["target_type"] = target_type
    if category_id:
        query["category_id"] = category_id
    items = get_collection(Q_COLLECTION).find(query).sort("sort", 1)
    return serialize_list(list(items))


@router.post("/questions")
def create_question(data: dict):
    data.setdefault("sort", 0)
    data.setdefault("active", True)
    result = get_collection(Q_COLLECTION).insert_one(data)
    return {"id": str(result.inserted_id)}


@router.put("/questions/{q_id}")
def update_question(q_id: str, data: dict):
    data.pop("_id", None)
    data.pop("id", None)
    result = get_collection(Q_COLLECTION).update_one(
        {"_id": oid(q_id)}, {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "问题不存在")
    return {"updated": True}


@router.delete("/questions/{q_id}")
def delete_question(q_id: str):
    get_collection(Q_COLLECTION).update_one(
        {"_id": oid(q_id)}, {"$set": {"active": False}}
    )
    return {"deleted": True}


# ---------- 答案 ----------
@router.get("/answers/{target_type}/{target_id}")
def get_answers(target_type: str, target_id: str):
    items = get_collection(A_COLLECTION).find(
        {"target_type": target_type, "target_id": target_id}
    )
    return serialize_list(list(items))


@router.post("/answers/{target_type}/{target_id}")
def save_answers(target_type: str, target_id: str, answers: list[dict]):
    """answers: [{"question_id","option","note","photo"}]，按 target_id+question_id upsert。"""
    col = get_collection(A_COLLECTION)
    q_col = get_collection(Q_COLLECTION)
    saved = 0
    for ans in answers:
        qid = ans.get("question_id", "")
        q = q_col.find_one({"_id": oid(qid)}) if qid else None
        if not q:
            continue
        # 空行（无答案/无备注/无照片）跳过，不保存
        if not any([ans.get("option"), ans.get("note"), ans.get("photo")]):
            continue
        payload = {
            "target_type": target_type,
            "target_id": target_id,
            "question_id": qid,
            "category_id": q.get("category_id"),
            "question_text": q.get("question_text"),
            "option": ans.get("option"),
            "note": ans.get("note"),
            "photo": ans.get("photo"),
            "updated_at": _now(),
        }
        col.update_one(
            {"target_id": target_id, "question_id": qid},
            {"$set": payload, "$setOnInsert": {"created_at": _now()}},
            upsert=True,
        )
        saved += 1
    return {"saved": saved}
