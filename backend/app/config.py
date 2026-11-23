"""应用配置：通过环境变量覆盖默认值。"""
import os
from pathlib import Path

# 项目根目录（backend/ 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "house_manager")

# 媒体存储根目录：放在用户目录下，不进入 git 仓库
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "/home/admin/house-media"))

# 服务监听
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 图片压缩参数
IMAGE_MAX_SIZE = 2048  # 原图最长边
THUMB_MAX_SIZE = 400    # 缩略图最长边
IMAGE_QUALITY = 75
