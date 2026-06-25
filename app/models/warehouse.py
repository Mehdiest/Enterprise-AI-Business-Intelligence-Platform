
from uuid import uuid4
from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_mixin
from sqlalchemy.sql import func
from app.database import Base

@declarative_mixin
class AuditMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class DimCustomer(Base, AuditMixin):
    __tablename__ = "dim_customer"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_code = Column(String(100), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)

class DimProduct(Base, AuditMixin):
    __tablename__ = "dim_product"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_code = Column(String(100), unique=True, nullable=False, index=True)
    product_name = Column(String(255), nullable=False)

class DimRegion(Base, AuditMixin):
    __tablename__ = "dim_region"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    region_name = Column(String(255), unique=True, nullable=False)

class DimChannel(Base, AuditMixin):
    __tablename__ = "dim_channel"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    channel_name = Column(String(255), unique=True, nullable=False)

class DimDate(Base):
    __tablename__ = "dim_date"
    id = Column(Integer, primary_key=True)
    full_date = Column(Date, unique=True, nullable=False)

class FactSales(Base, AuditMixin):
    __tablename__ = "fact_sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("dim_customer.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("dim_product.id"), nullable=False)
    region_id = Column(UUID(as_uuid=True), ForeignKey("dim_region.id"), nullable=False)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("dim_channel.id"), nullable=False)
    date_id = Column(Integer, ForeignKey("dim_date.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    amount = Column(Numeric(12,2), nullable=False)

    customer = relationship("DimCustomer")
    product = relationship("DimProduct")
    region = relationship("DimRegion")
    channel = relationship("DimChannel")
    date = relationship("DimDate")

Index("ix_fact_sales_date", FactSales.date_id)
Index("ix_fact_sales_customer", FactSales.customer_id)
