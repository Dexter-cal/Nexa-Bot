from sqlalchemy import Column, String, Boolean, Integer, JSON, ForeignKey, DateTime, DECIMAL, Text, func
from nexa.models.base import Base, TimestampMixin, generate_uuid

class Tool(Base, TimestampMixin):
    __tablename__ = 'tools'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    description = Column(Text)
    category = Column(String)

    risk_level = Column(String, default='low')
    requires_approval = Column(Boolean, default=False)

    implementation_type = Column(String, default='python')
    code = Column(Text)
    module_path = Column(String)

    parameters_schema = Column(JSON)
    is_enabled = Column(Boolean, default=True)

class Guardrail(Base, TimestampMixin):
    __tablename__ = 'guardrails'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    rule_text = Column(Text, nullable=False)
    rule_type = Column(String, nullable=False)
    condition = Column(JSON, nullable=False)
    action = Column(String, default='block')
    priority = Column(Integer, default=100)
    is_enabled = Column(Boolean, default=True)

class Action(Base):
    __tablename__ = 'actions'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='SET NULL'))
    task_id = Column(String, ForeignKey('tasks.id', ondelete='CASCADE'))

    action_type = Column(String, nullable=False)
    description = Column(Text)
    parameters = Column(JSON)
    result = Column(JSON)
    status = Column(String, default='success')
    executed_at = Column(DateTime, default=func.now())

class LLMUsage(Base):
    __tablename__ = 'llm_usage'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = Column(String, ForeignKey('tasks.id', ondelete='SET NULL'))

    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    cost_usd = Column(DECIMAL(10, 6), nullable=False)
    created_at = Column(DateTime, default=func.now())
