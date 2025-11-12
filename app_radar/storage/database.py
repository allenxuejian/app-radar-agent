"""
App Radar Agent - 数据库模型
使用 SQLAlchemy ORM 实现数据持久化
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app_radar.config.settings import settings

Base = declarative_base()


class App(Base):
    """应用基础信息表"""
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_identifier = Column(String, unique=True, nullable=False, index=True)  # trackId or bundle_id
    name = Column(String, nullable=False)
    platform = Column(String, default='ios')  # 'ios' or 'android'
    developer = Column(String)
    category = Column(String)
    url = Column(String)
    first_tracked_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    metrics = relationship("Metric", back_populates="app", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<App(id={self.id}, name='{self.name}', platform='{self.platform}')>"


class Metric(Base):
    """应用指标历史记录表"""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, ForeignKey('apps.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 基础指标
    rating = Column(Float)
    rating_count = Column(Integer)
    version = Column(String)

    # 估算指标
    estimated_dau = Column(Integer)
    estimated_mau = Column(Integer)

    # 榜单数据
    rank_overall = Column(Integer)
    rank_category = Column(Integer)

    # 元数据
    source = Column(String, default='itunes')  # 数据来源
    confidence = Column(Float, default=1.0)  # 数据可信度 0-1

    # Relationships
    app = relationship("App", back_populates="metrics")

    def __repr__(self):
        return f"<Metric(app_id={self.app_id}, rating={self.rating}, timestamp={self.timestamp})>"


class CompanyInfo(Base):
    """公司信息表"""
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String, unique=True, nullable=False)
    employee_count_min = Column(Integer)
    employee_count_max = Column(Integer)
    funding_total = Column(Float)
    funding_stage = Column(String)
    last_funding_date = Column(DateTime)
    headquarters = Column(String)
    founded_year = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CompanyInfo(name='{self.company_name}', funding=${self.funding_total})>"


# === 数据库引擎和会话 ===
engine = create_engine(
    settings.database_url,
    echo=False,  # 设为 True 可查看 SQL 语句
    connect_args={"check_same_thread": False}  # SQLite 需要
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库 - 创建所有表"""
    Base.metadata.create_all(engine)
    print("✅ Database initialized successfully")


def get_db():
    """获取数据库会话 - 使用上下文管理器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """获取数据库会话 - 直接返回"""
    return SessionLocal()
