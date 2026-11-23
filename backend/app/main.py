"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import MEDIA_ROOT
from .routers import (
    community,
    listing,
    photo,
    score,
    field_template,
    question,
    upload,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时写入种子数据（若集合为空）
    from .seed import init_seed

    init_seed()
    yield


app = FastAPI(title="房产管理系统", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载媒体静态目录（图片/视频通过 /media/xxx 访问）
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT)), name="media")

app.include_router(community.router, prefix="/api/community", tags=["小区"])
app.include_router(listing.router, prefix="/api/listing", tags=["房源"])
app.include_router(photo.router, prefix="/api/photo", tags=["照片"])
app.include_router(score.router, prefix="/api/score", tags=["评分"])
app.include_router(field_template.router, prefix="/api/field-template", tags=["字段模板"])
app.include_router(question.router, prefix="/api/question", tags=["评分问题"])
app.include_router(upload.router, prefix="/api/upload", tags=["上传"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
