"""字段模板维护：定义小区/房源有哪些基本信息字段。"""
from fastapi import APIRouter, HTTPException, Query

from ..database import get_collection
from ..utils import oid, serialize, serialize_list

router = APIRouter()
COLLECTION = "field_template"


@router.get("")
def list_field_templates(target_type: str = Query("community")):
    items = get_collection(COLLECTION).find(
        {"target_type": target_type, "active": {"$ne": False}}
    ).sort("sort", 1)
    return serialize_list(list(items))


@router.post("")
def create_field_template(data: dict):
    if not data.get("field_key") or not data.get("field_label"):
        raise HTTPException(400, "field_key 和 field_label 必填")
    data.setdefault("target_type", "community")
    data.setdefault("field_type", "text")
    data.setdefault("sort", 0)
    data.setdefault("required", False)
    data.setdefault("active", True)
    result = get_collection(COLLECTION).insert_one(data)
    return {"id": str(result.inserted_id)}


@router.put("/{field_id}")
def update_field_template(field_id: str, data: dict):
    data.pop("_id", None)
    data.pop("id", None)
    result = get_collection(COLLECTION).update_one(
        {"_id": oid(field_id)}, {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "字段模板不存在")
    return {"updated": True}


@router.delete("/{field_id}")
def delete_field_template(field_id: str):
    # 软删除，保留历史数据
    result = get_collection(COLLECTION).update_one(
        {"_id": oid(field_id)}, {"$set": {"active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "字段模板不存在")
    return {"deleted": True}
