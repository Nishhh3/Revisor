import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.database import Base

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository = Column(String, nullable=False)
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(String, nullable=True)    
    pr_author_hash = Column(String, nullable=True)  # hashed -- see review_store.py
    finding_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    findings = relationship("Finding", back_populates="review", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="review", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False)
    agent_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    issue = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    line = Column(Integer, nullable=True)
    evidence = Column(JSONB, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("Review", back_populates="findings")

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # ok | error
    duration_ms = Column(Integer, nullable=True)
    findings_raw = Column(Integer, default=0)   # returned by the model
    findings_kept = Column(Integer, default=0)  # after filters and validation
    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("Review", back_populates="agent_runs")