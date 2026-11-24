"""文件上传：直接存储（图片已在浏览器本地压缩后再上传，服务端不再处理）。"""
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from ..database import get_collection
from ..storage import storage

router = APIRouter()


@router.post("")
async def upload_file(
    target_type: str = Form(...),
    target_id: str = Form(...),
    caption: str = Form(None),
    save_record: bool = Form(True),
    file: UploadFile = File(...),
):
    data = await file.read()
    ext = Path(file.filename or "").suffix.lower() or ".bin"
    file_key = f"{target_type}/{target_id}/{uuid.uuid4().hex}{ext}"
    storage.save(data, file_key)

    url = storage.get_url(file_key)

    result_data = {
        "file_key": file_key,
        "url": url,
        "thumb_url": None,
    }

    # save_record=False 时（如问答照片）只存文件，不写入照片记录集合
    if save_record:
        photo = {
            "target_type": target_type,
            "target_id": target_id,
            "file_key": file_key,
            "url": url,
            "thumb_url": None,
            "caption": caption,
            "sort": 0,
            "created_at": datetime.now(timezone.utc),
        }
        res = get_collection("photo").insert_one(photo)
        result_data["id"] = str(res.inserted_id)

    return result_data
