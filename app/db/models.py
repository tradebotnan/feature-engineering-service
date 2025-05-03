from sqlalchemy import Column, Integer, String, Date, Enum, Boolean, DateTime
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class StatusEnum(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    error = "error"

class FeatureDispatchLog(Base):
    __tablename__ = "feature_dispatch_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    asset_class = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    features_path = Column(String, nullable=True)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.pending)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    is_live = Column(Boolean, nullable=False, default=False)