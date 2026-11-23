"""评分：保存答案、计算加权汇总。"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..database import get_collection
from ..utils import oid, serialize, serialize_list

router = APIRouter()
REC_COLLECTION = "score_record"


def _now():
    return datetime.now(timezone.utc)


def _recalc(community_id: str):
    """根据评分记录重算综合分与各维度分，并回写小区文档。"""
    records = list(get_collection(REC_COLLECTION).find({"community_id": community_id}))
    categories = list(get_collection("score_category").find({"active": {"$ne": False}}))
    cat_map = {str(c["_id"]): c for c in categories}

    cat_scores: dict[str, list] = {}
    for r in records:
        cid = r.get("category_id")
        score = (r.get("option") or {}).get("score")
        if cid is None or score is None:
            continue
        cat_scores.setdefault(cid, []).append(score)

    total_weighted = 0.0
    total_weight = 0.0
    detail = {}
    for cid, scores in cat_scores.items():
        avg = sum(scores) / len(scores)
        weight = cat_map.get(cid, {}).get("weight", 1.0)
        name = cat_map.get(cid, {}).get("name", cid)
        detail[name] = round(avg, 2)
        total_weighted += avg * weight
        total_weight += weight

    score_avg = round(total_weighted / total_weight, 2) if total_weight > 0 else None
    get_collection("community").update_one(
        {"_id": oid(community_id)},
        {"$set": {"score_avg": score_avg, "score_detail": detail, "updated_at": _now()}},
    )
    return {"score_avg": score_avg, "score_detail": detail}


@router.get("/{community_id}")
def get_scores(community_id: str):
    records = list(get_collection(REC_COLLECTION).find({"community_id": community_id}))
    return serialize_list(records)


@router.post("/{community_id}")
def save_scores(community_id: str, answers: list[dict]):
    """answers: [{"question_id": "...", "option": {"text": "满意", "score": 4}}, ...]"""
    q_col = get_collection("score_question")
    rec_col = get_collection(REC_COLLECTION)
    for ans in answers:
        q = q_col.find_one({"_id": oid(ans.get("question_id", ""))})
        if not q:
            continue
        rec_col.update_one(
            {"community_id": community_id, "question_id": ans["question_id"]},
            {
                "$set": {
                    "category_id": q.get("category_id"),
                    "question_text": q.get("question_text"),
                    "option": ans.get("option"),
                    "updated_at": _now(),
                },
                "$setOnInsert": {"created_at": _now()},
            },
            upsert=True,
        )
    summary = _recalc(community_id)
    return {"saved": True, **summary}


@router.get("/summary/{community_id}")
def score_summary(community_id: str):
    c = get_collection("community").find_one({"_id": oid(community_id)})
    if not c:
        raise HTTPException(404, "小区不存在")
    records = list(get_collection(REC_COLLECTION).find({"community_id": community_id}))
    return {
        "score_avg": c.get("score_avg"),
        "score_detail": c.get("score_detail", {}),
        "records": serialize_list(records),
    }
