"""小区 CRUD（动态字段直接平铺存储）。"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..database import get_collection
from ..utils import oid, serialize, serialize_list

router = APIRouter()
COLLECTION = "community"


def _now():
    return datetime.now(timezone.utc)


@router.get("")
def list_communities():
    items = list(get_collection(COLLECTION).find().sort("created_at", -1))
    result = []
    photo_col = get_collection("photo")
    listing_col = get_collection("listing")
    for c in items:
        cid = str(c["_id"])
        c = serialize(c)
        c["photo_count"] = photo_col.count_documents(
            {"target_type": "community", "target_id": cid}
        )
        c["listing_count"] = listing_col.count_documents({"community_id": cid})
        result.append(c)
    return result


@router.get("/{community_id}")
def get_community(community_id: str):
    c = get_collection(COLLECTION).find_one({"_id": oid(community_id)})
    if not c:
        raise HTTPException(404, "小区不存在")
    c = serialize(c)
    c["photos"] = serialize_list(list(
        get_collection("photo").find(
            {"target_type": "community", "target_id": community_id}
        ).sort("sort", 1)
    ))
    c["listings"] = serialize_list(list(
        get_collection("listing").find({"community_id": community_id}).sort("created_at", -1)
    ))
    return c


@router.post("")
def create_community(data: dict):
    if not data.get("name"):
        raise HTTPException(400, "小区名称必填")
    data["created_at"] = _now()
    data["updated_at"] = _now()
    data.setdefault("score_avg", None)
    result = get_collection(COLLECTION).insert_one(data)
    return {"id": str(result.inserted_id)}


@router.put("/{community_id}")
def update_community(community_id: str, data: dict):
    data.pop("_id", None)
    data.pop("id", None)
    data.pop("created_at", None)
    data["updated_at"] = _now()
    result = get_collection(COLLECTION).update_one(
        {"_id": oid(community_id)}, {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "小区不存在")
    return {"updated": True}


@router.delete("/{community_id}")
def delete_community(community_id: str):
    result = get_collection(COLLECTION).delete_one({"_id": oid(community_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "小区不存在")
    # 级联删除房源、照片
    get_collection("listing").delete_many({"community_id": community_id})
    get_collection("photo").delete_many(
        {"target_type": "community", "target_id": community_id}
    )
    get_collection("score_record").delete_many({"community_id": community_id})
    return {"deleted": True}
