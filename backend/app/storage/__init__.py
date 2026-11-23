"""存储抽象层：默认使用本地文件系统，后续可扩展对象存储。"""
from .local import LocalStorage
from ..config import MEDIA_ROOT

storage = LocalStorage(MEDIA_ROOT)
