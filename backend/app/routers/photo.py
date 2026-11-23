"""照片记录管理（也可直接由上传接口写入）。"""
from fastapi import APIRouter, HTTPException, Query

from ..database import get_collection
from ..utils import oid, serialize, serialize_list

router = APIRouter()
COLLECTION = "photo"


@router.get("")
def list_photos(target_type: str, target_id: str):
    items = get_collection(COLLECTION).find(
        {"target_type": target_type, "target_id": target_id}
    ).sort("sort", 1)
    return serialize_list(list(items))


@router.post("")
def create_photo(data: dict):
    if not data.get("target_type") or not data.get("target_id"):
        raise HTTPException(400, "target_type 和 target_id 必填")
    data.setdefault("sort", 0)
    result = get_collection(COLLECTION).insert_one(data)
    return {"id": str(result.inserted_id)}


@router.put("/{photo_id}")
def update_photo(photo_id: str, data: dict):
    data.pop("_id", None)
    data.pop("id", None)
    result = get_collection(COLLECTION).update_one(
        {"_id": oid(photo_id)}, {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "照片不存在")
    return {"updated": True}


@router.delete("/{photo_id}")
def delete_photo(photo_id: str):
    result = get_collection(COLLECTION).delete_one({"_id": oid(photo_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "照片不存在")
    return {"deleted": True}
