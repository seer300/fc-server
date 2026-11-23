"""Pydantic 数据模型（用于请求校验与 API 文档）。"""
from typing import Optional
from pydantic import BaseModel, Field


class FieldTemplateIn(BaseModel):
    target_type: str = Field(..., description="community 或 listing")
    field_key: str = Field(..., description="字段唯一标识")
    field_label: str = Field(..., description="字段显示名称")
    field_type: str = Field("text", description="text/number/select/date/textarea")
    options: Optional[list] = Field(None, description="select 类型的选项列表")
    default_value: Optional[str] = None
    sort: int = 0
    required: bool = False
    active: bool = True


class ScoreCategoryIn(BaseModel):
    name: str
    weight: float = 1.0
    sort: int = 0
    active: bool = True


class ScoreQuestionIn(BaseModel):
    category_id: str
    question_text: str
    question_type: str = "single"
    options: list = Field(..., description='[{"text":"满意","score":4}, ...]')
    sort: int = 0
    active: bool = True


class ScoreAnswer(BaseModel):
    question_id: str
    option: dict  # 快照：{"text":"满意","score":4}
