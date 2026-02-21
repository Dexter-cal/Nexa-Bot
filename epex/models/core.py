from sqlalchemy import Column, String, Boolean, Integer, JSON, ForeignKey, DateTime, DECIMAL, Text
from sqlalchemy.orm import relationship
from epex.models.base import Base, TimestampMixin, generate_uuid

class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    display_name = Column(String)
    phone_number = Column(String)
    timezone = Column(String, default='UTC')

    preferences = Column(JSON, default={})
    epex_name = Column(String, default='Epex')
    user_title = Column(String)
    personality_mode = Column(String, default='professional')

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    tasks = relationship("Task", back_populates="user")

class Session(Base, TimestampMixin):
    __tablename__ = 'sessions'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    access_token = Column(String, unique=True, nullable=False)
    refresh_token = Column(String, unique=True)
    device_info = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(Text)

    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

class Task(Base, TimestampMixin):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text)
    command = Column(Text)
    task_type = Column(String)

    status = Column(String, default='pending')
    priority = Column(String, default='medium')
    progress = Column(DECIMAL(5, 4), default=0)

    execution_plan = Column(JSON)
    risk_level = Column(String, default='low')
    requires_approval = Column(Boolean, default=False)

    model_used = Column(String)
    provider = Column(String)

    result = Column(JSON)
    output = Column(Text)
    error_message = Column(Text)

    user = relationship("User", back_populates="tasks")
