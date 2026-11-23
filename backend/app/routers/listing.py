"""房源 CRUD。"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from ..database import get_collection
from ..utils import oid, serialize, serialize_list

router = APIRouter()
COLLECTION = "listing"


def _now():
    return datetime.now(timezone.utc)


@router.get("")
def list_listings(community_id: str | None = Query(None)):
    query = {}
    if community_id:
        query["community_id"] = community_id
    items = list(get_collection(COLLECTION).find(query).sort("created_at", -1))
    result = []
    photo_col = get_collection("photo")
    for it in items:
        lid = str(it["_id"])
        it = serialize(it)
        it["photo_count"] = photo_col.count_documents(
            {"target_type": "listing", "target_id": lid}
        )
        result.append(it)
    return result


@router.get("/{listing_id}")
def get_listing(listing_id: str):
    it = get_collection(COLLECTION).find_one({"_id": oid(listing_id)})
    if not it:
        raise HTTPException(404, "房源不存在")
    it = serialize(it)
    it["photos"] = serialize_list(list(
        get_collection("photo").find(
            {"target_type": "listing", "target_id": listing_id}
        ).sort("sort", 1)
    ))
    return it


@router.post("")
def create_listing(data: dict):
    if not data.get("community_id"):
        raise HTTPException(400, "community_id 必填")
    data["created_at"] = _now()
    data["updated_at"] = _now()
    result = get_collection(COLLECTION).insert_one(data)
    return {"id": str(result.inserted_id)}


@router.put("/{listing_id}")
def update_listing(listing_id: str, data: dict):
    data.pop("_id", None)
    data.pop("id", None)
    data.pop("created_at", None)
    data["updated_at"] = _now()
    result = get_collection(COLLECTION).update_one(
        {"_id": oid(listing_id)}, {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "房源不存在")
    return {"updated": True}


@router.delete("/{listing_id}")
def delete_listing(listing_id: str):
    result = get_collection(COLLECTION).delete_one({"_id": oid(listing_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "房源不存在")
    get_collection("photo").delete_many(
        {"target_type": "listing", "target_id": listing_id}
    )
    return {"deleted": True}
