from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date


# 用户相关
class UserBase(BaseModel):
    username: str
    email: EmailStr
    user_type: str = "individual"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# 案例相关
class CaseBase(BaseModel):
    case_number: str
    title: str
    court: Optional[str] = None
    case_type: Optional[str] = None
    judgment_date: Optional[date] = None
    content: str
    parties: Optional[dict] = None
    legal_basis: Optional[list] = None
    is_real: Optional[str] = "example"  # real: 真实案例, example: 教学示例
    source: Optional[str] = None  # 数据来源


class CaseCreate(CaseBase):
    pass


class CaseResponse(CaseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 搜索相关
class SearchRequest(BaseModel):
    query: str
    filters: Optional[dict] = None
    page: int = 1
    page_size: int = 20


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[CaseResponse]


# 案例分析
class AnalysisRequest(BaseModel):
    case_id: int


class AnalysisResponse(BaseModel):
    case_id: int
    summary: str
    summary_plain: Optional[str] = None
    key_elements: dict
    key_elements_plain: Optional[dict] = None
    legal_reasoning: str
    legal_reasoning_plain: Optional[str] = None
    legal_basis: list[str]
    legal_basis_plain: Optional[list[str]] = None
    judgment_result: str
    judgment_result_plain: Optional[str] = None
    plain_language_tips: Optional[str] = None
