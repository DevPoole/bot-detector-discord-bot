from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR, DATETIME
from datetime import datetime

from src.core.database import Base


class discordEvent(Base):
    __tablename__ = "discordEvent"
    id = Column("id", Integer, primary_key=True)
    created_at = Column("created_at", DATETIME, default=datetime.utcnow)
    updated_at = Column("updated_at", DATETIME, onupdate=datetime.utcnow)
    event_name = Column("event_name", VARCHAR(50), unique=True)
    active = Column("active", TINYINT, default=1)
