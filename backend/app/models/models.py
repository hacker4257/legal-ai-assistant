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


class LegalStatute(Base):
    """法律条文模型 - RAG 知识库核心"""
    __tablename__ = "legal_statutes"

    id = Column(Integer, primary_key=True, index=True)
    law_name = Column(String(200), nullable=False, index=True)  # 法律名称，如"中华人民共和国民法典"
    law_category = Column(String(50), index=True)  # 法律类别：民法、刑法、行政法、劳动法等
    chapter = Column(String(200))  # 章节，如"第三编 合同"
    article_number = Column(String(50), nullable=False, index=True)  # 条款号，如"第五百零九条"
    article_title = Column(String(200))  # 条款标题（如有）
    content = Column(Text, nullable=False)  # 条文内容
    keywords = Column(JSON)  # 关键词标签，用于检索增强
    effective_date = Column(Date)  # 生效日期
    source = Column(String(200))  # 来源
    created_at = Column(DateTime, default=datetime.utcnow)


class JudicialInterpretation(Base):
    """司法解释模型"""
    __tablename__ = "judicial_interpretations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)  # 标题
    issuing_authority = Column(String(100))  # 发布机关，如"最高人民法院"
    document_number = Column(String(100), index=True)  # 文号，如"法释〔2020〕17号"
    category = Column(String(50), index=True)  # 类别：民事、刑事、行政等
    related_laws = Column(JSON)  # 关联的法律名称
    content = Column(Text, nullable=False)  # 内容
    summary = Column(Text)  # 摘要
    effective_date = Column(Date)  # 生效日期
    source = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


class RetrievalLog(Base):
    """RAG 检索日志 - 用于溯源和优化"""
    __tablename__ = "retrieval_logs"

    id = Column(Integer, primary_key=True, index=True)
    case_analysis_id = Column(Integer, index=True)  # 关联的分析记录
    query_text = Column(Text)  # 检索查询
    retrieved_statutes = Column(JSON)  # 检索到的法条 [{id, score, content}]
    retrieved_cases = Column(JSON)  # 检索到的案例
    retrieved_interpretations = Column(JSON)  # 检索到的司法解释
    rerank_scores = Column(JSON)  # 重排序分数
    created_at = Column(DateTime, default=datetime.utcnow)
