"""文件上传：图片自动压缩并生成缩略图，视频等直接存储；上传后写入照片记录。"""
import io
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from PIL import Image

from ..config import IMAGE_MAX_SIZE, IMAGE_QUALITY, THUMB_MAX_SIZE
from ..database import get_collection
from ..storage import storage

router = APIRouter()

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".bmp"}


def _compress(data: bytes, max_size: int, quality: int) -> bytes:
    img = Image.open(io.BytesIO(data))
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


@router.post("")
async def upload_file(
    target_type: str = Form(...),
    target_id: str = Form(...),
    caption: str = Form(None),
    file: UploadFile = File(...),
):
    data = await file.read()
    ext = Path(file.filename or "").suffix.lower()
    is_image = ext in IMAGE_EXT

    thumb_url = None
    if is_image:
        try:
            data = _compress(data, IMAGE_MAX_SIZE, IMAGE_QUALITY)
            file_key = f"{target_type}/{target_id}/{uuid.uuid4().hex}.jpg"
            storage.save(data, file_key)

            thumb_data = _compress(data, THUMB_MAX_SIZE, IMAGE_QUALITY)
            thumb_key = f"thumb/{target_type}/{target_id}/{uuid.uuid4().hex}.jpg"
            storage.save(thumb_data, thumb_key)
            thumb_url = storage.get_url(thumb_key)
        except Exception:
            file_key = f"{target_type}/{target_id}/{uuid.uuid4().hex}{ext or '.jpg'}"
            storage.save(data, file_key)
    else:
        file_key = f"{target_type}/{target_id}/{uuid.uuid4().hex}{ext or '.bin'}"
        storage.save(data, file_key)

    url = storage.get_url(file_key)

    # 写入照片记录
    photo = {
        "target_type": target_type,
        "target_id": target_id,
        "file_key": file_key,
        "url": url,
        "thumb_url": thumb_url,
        "caption": caption,
        "sort": 0,
        "created_at": datetime.now(timezone.utc),
    }
    result = get_collection("photo").insert_one(photo)
    photo["id"] = str(result.inserted_id)
    del photo["_id"]

    return photo
