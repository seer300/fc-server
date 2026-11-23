"""本地文件系统存储实现。"""
from pathlib import Path

from .base import Storage


class LocalStorage(Storage):
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, file_key: str) -> str:
        path = self.root / file_key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return file_key

    def get_url(self, file_key: str) -> str:
        # 通过 FastAPI 挂载的 /media 静态目录访问
        return f"/media/{file_key}"

    def delete(self, file_key: str) -> None:
        path = self.root / file_key
        if path.exists():
            path.unlink()
