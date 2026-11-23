"""存储抽象接口：本地存储与对象存储共用此接口，方便后续切换。"""
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, data: bytes, file_key: str) -> str:
        """保存文件内容，返回 file_key。"""

    @abstractmethod
    def get_url(self, file_key: str) -> str:
        """返回文件的访问 URL 路径。"""

    @abstractmethod
    def delete(self, file_key: str) -> None:
        """删除文件。"""
