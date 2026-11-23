"""初始化种子数据：首次启动时，若集合为空则写入示例字段模板与评分问题模板。"""
from .database import get_collection

# 五档评分选项（通用）
FIVE_LEVEL_OPTIONS = [
    {"text": "非常满意", "score": 5},
    {"text": "满意", "score": 4},
    {"text": "一般", "score": 3},
    {"text": "不满", "score": 2},
    {"text": "很差", "score": 1},
]

# 小区字段模板
COMMUNITY_FIELDS = [
    {"target_type": "community", "field_key": "developer", "field_label": "开发商", "field_type": "text", "sort": 1},
    {"target_type": "community", "field_key": "build_year", "field_label": "建成年代", "field_type": "number", "sort": 2},
    {"target_type": "community", "field_key": "greening_rate", "field_label": "绿化率(%)", "field_type": "number", "sort": 3},
    {"target_type": "community", "field_key": "plot_ratio", "field_label": "容积率", "field_type": "number", "sort": 4},
    {"target_type": "community", "field_key": "property_fee", "field_label": "物业费(元/㎡)", "field_type": "number", "sort": 5},
    {"target_type": "community", "field_key": "parking_type", "field_label": "车位类型", "field_type": "select", "options": [{"label": "地下车库", "value": "地下车库"}, {"label": "地上车位", "value": "地上车位"}, {"label": "人车分流", "value": "人车分流"}, {"label": "无车位", "value": "无车位"}], "sort": 6},
    {"target_type": "community", "field_key": "school", "field_label": "对口学校", "field_type": "text", "sort": 7},
]

# 房源字段模板
LISTING_FIELDS = [
    {"target_type": "listing", "field_key": "price", "field_label": "总价(万)", "field_type": "number", "sort": 1},
    {"target_type": "listing", "field_key": "area", "field_label": "面积(㎡)", "field_type": "number", "sort": 2},
    {"target_type": "listing", "field_key": "rooms", "field_label": "户型", "field_type": "select", "options": [{"label": "一室", "value": "一室"}, {"label": "两室", "value": "两室"}, {"label": "三室", "value": "三室"}, {"label": "四室及以上", "value": "四室及以上"}], "sort": 3},
    {"target_type": "listing", "field_key": "floor", "field_label": "楼层", "field_type": "text", "sort": 4},
    {"target_type": "listing", "field_key": "direction", "field_label": "朝向", "field_type": "select", "options": [{"label": "南", "value": "南"}, {"label": "东南", "value": "东南"}, {"label": "东", "value": "东"}, {"label": "南北", "value": "南北"}, {"label": "西", "value": "西"}, {"label": "北", "value": "北"}], "sort": 5},
    {"target_type": "listing", "field_key": "decoration", "field_label": "装修", "field_type": "select", "options": [{"label": "毛坯", "value": "毛坯"}, {"label": "简装", "value": "简装"}, {"label": "精装", "value": "精装"}, {"label": "豪装", "value": "豪装"}], "sort": 6},
]

# 评分类别与问题
SCORE_CATEGORIES = [
    {"name": "地段交通", "weight": 1.5, "sort": 1,
     "questions": [
         {"question_text": "离地铁/公交步行时间", "options": FIVE_LEVEL_OPTIONS},
         {"question_text": "周边生活配套完善度", "options": FIVE_LEVEL_OPTIONS},
         {"question_text": "周边噪音情况", "options": FIVE_LEVEL_OPTIONS},
     ]},
    {"name": "物业管理", "weight": 1.0, "sort": 2,
     "questions": [
         {"question_text": "物业费水平合理性", "options": FIVE_LEVEL_OPTIONS},
         {"question_text": "安保情况", "options": FIVE_LEVEL_OPTIONS},
         {"question_text": "绿化与卫生维护", "options": FIVE_LEVEL_OPTIONS},
     ]},
    {"name": "房屋品质", "weight": 1.0, "sort": 3,
     "questions": [
         {"question_text": "户型设计合理性", "options": FIVE_LEVEL_OPTIONS},
         {"question_text": "采光通风", "options": FIVE_LEVEL_OPTIONS},
         {"question_text": "隔音效果", "options": FIVE_LEVEL_OPTIONS},
     ]},
]


def init_seed():
    """各集合为空时才写入种子数据，避免覆盖用户已有配置。"""
    ft_col = get_collection("field_template")
    if ft_col.count_documents({}) == 0:
        ft_col.insert_many(COMMUNITY_FIELDS + LISTING_FIELDS)

    cat_col = get_collection("score_category")
    q_col = get_collection("score_question")
    if cat_col.count_documents({}) == 0:
        for c in SCORE_CATEGORIES:
            questions = c.pop("questions", [])
            cat_id = cat_col.insert_one(c).inserted_id
            for i, q in enumerate(questions):
                q_col.insert_one({
                    "category_id": str(cat_id),
                    "question_text": q["question_text"],
                    "question_type": "single",
                    "options": q["options"],
                    "sort": i + 1,
                    "active": True,
                })
