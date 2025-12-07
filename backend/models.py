from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    REVIEWER = "reviewer"
    VIEWER = "viewer"

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    STANDARD = "standard"
    PROFESSIONAL = "professional"

class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"

class FieldType(str, enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    DROPDOWN = "dropdown"
    FILE = "file"
    CHECKBOX = "checkbox"
    EMAIL = "email"
    PHONE = "phone"

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    tenant = relationship("Tenant", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user")
    documents = relationship("Document", back_populates="uploaded_by_user")

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="tenant")
    subscription = relationship("Subscription", back_populates="tenant", uselist=False)
    form_schemas = relationship("FormSchema", back_populates="tenant")
    documents = relationship("Document", back_populates="tenant")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(SQLEnum(UserRole), nullable=False)
    description = Column(Text)
    permissions = Column(JSON)  # Store permissions as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_roles = relationship("UserRole", back_populates="role")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), unique=True, nullable=False)
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    max_pages_per_month = Column(Integer, default=100)
    current_month_usage = Column(Integer, default=0)
    razorpay_subscription_id = Column(String(255))
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="subscription")
    billing_usage = relationship("BillingUsage", back_populates="subscription")

class FormSchema(Base):
    __tablename__ = "form_schemas"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="form_schemas")
    fields = relationship("FormField", back_populates="schema")
    documents = relationship("Document", back_populates="form_schema")

class FormField(Base):
    __tablename__ = "form_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    schema_id = Column(Integer, ForeignKey("form_schemas.id"), nullable=False)
    field_name = Column(String(255), nullable=False)
    field_label = Column(String(255), nullable=False)
    field_type = Column(SQLEnum(FieldType), nullable=False)
    is_required = Column(Boolean, default=False)
    default_value = Column(String(255))
    regex_validation = Column(String(500))
    dropdown_options = Column(JSON)  # For dropdown field types
    cross_field_rules = Column(JSON)  # Validation rules with other fields
    field_group = Column(String(255))  # For grouping fields into sections
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    schema = relationship("FormSchema", back_populates="fields")
    field_values = relationship("FieldValue", back_populates="field")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    form_schema_id = Column(Integer, ForeignKey("form_schemas.id"))
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)  # S3 path
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    num_pages = Column(Integer, default=1)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)
    overall_confidence = Column(Float, default=0.0)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="documents")
    form_schema = relationship("FormSchema", back_populates="documents")
    uploaded_by_user = relationship("User", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document")
    field_values = relationship("FieldValue", back_populates="document")
    processing_logs = relationship("ProcessingLog", back_populates="document")

class DocumentPage(Base):
    __tablename__ = "document_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String(1000))  # S3 path for page image
    preprocessed_path = Column(String(1000))  # Preprocessed image path
    quality_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="pages")
    ocr_results = relationship("OCRResult", back_populates="page")
    llm_results = relationship("LLMResult", back_populates="page")

class OCRResult(Base):
    __tablename__ = "ocr_results"
    
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("document_pages.id"), nullable=False)
    ocr_engine = Column(String(50), nullable=False)  # tesseract, rapidocr, paddleocr, etc.
    extracted_text = Column(Text)
    confidence_score = Column(Float, default=0.0)
    bounding_boxes = Column(JSON)  # Store coordinates
    processing_time = Column(Float)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    page = relationship("DocumentPage", back_populates="ocr_results")

class LLMResult(Base):
    __tablename__ = "llm_results"
    
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("document_pages.id"), nullable=False)
    llm_model = Column(String(100), nullable=False)  # deepseek, qwen, mistral, etc.
    input_text = Column(Text)
    normalized_output = Column(JSON)  # Structured JSON output
    confidence_score = Column(Float, default=0.0)
    processing_time = Column(Float)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    page = relationship("DocumentPage", back_populates="llm_results")

class FieldValue(Base):
    __tablename__ = "field_values"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    field_id = Column(Integer, ForeignKey("form_fields.id"), nullable=False)
    extracted_value = Column(Text)
    normalized_value = Column(Text)
    confidence_score = Column(Float, default=0.0)
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(JSON)
    needs_review = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    final_value = Column(Text)  # After human review/approval
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    document = relationship("Document", back_populates="field_values")
    field = relationship("FormField", back_populates="field_values")

class ProcessingLog(Base):
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    stage = Column(String(100), nullable=False)  # preprocessing, ocr, llm, validation
    message = Column(Text)
    log_metadata = Column(JSON)  # Additional data
    level = Column(String(20), default="INFO")  # INFO, WARNING, ERROR
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="processing_logs")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))  # document, schema, config, etc.
    resource_id = Column(Integer)
    changes = Column(JSON)  # Before/after values
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class BillingUsage(Base):
    __tablename__ = "billing_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"))
    pages_processed = Column(Integer, default=0)
    ocr_cost = Column(Float, default=0.0)
    llm_cost = Column(Float, default=0.0)
    cloud_ocr_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    billing_period_start = Column(DateTime)
    billing_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscription = relationship("Subscription", back_populates="billing_usage")

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(255), unique=True, nullable=False)
    config_value = Column(JSON)
    description = Column(Text)
    is_secret = Column(Boolean, default=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReviewQueue(Base):
    __tablename__ = "review_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    priority = Column(Integer, default=0)  # Higher number = higher priority
    reason = Column(String(500))  # Why it needs review
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
