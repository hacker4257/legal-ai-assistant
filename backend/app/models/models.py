from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Date
from app.db.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(20), default="individual")  # individual or enterprise
    created_at = Column(DateTime, default=datetime.utcnow)


class Case(Base):
    """案例模型"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), unique=True, index=True)
    title = Column(Text, nullable=False)
    court = Column(String(200))
    case_type = Column(String(50), index=True)
    judgment_date = Column(Date)
    content = Column(Text, nullable=False)
    parties = Column(JSON)  # 当事人信息
    legal_basis = Column(JSON)  # 法律依据
    is_real = Column(String(20), default="example")  # real: 真实案例, example: 教学示例
    source = Column(String(200))  # 数据来源，如"最高人民法院公报2020年第3期"
    created_at = Column(DateTime, default=datetime.utcnow)


class SearchHistory(Base):
    """搜索历史模型"""
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    query = Column(Text, nullable=False)
    filters = Column(JSON)
    results_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class Favorite(Base):
    """收藏模型"""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    case_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Note(Base):
    """笔记模型"""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    case_id = Column(Integer, index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CaseAnalysis(Base):
    """案例分析缓存"""
    __tablename__ = "case_analysis"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, unique=True, index=True, nullable=False)
    analysis_result = Column(JSON, nullable=False)  # 存储完整的分析结果
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
