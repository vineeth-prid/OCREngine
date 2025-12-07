from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import SubscriptionTier, DocumentStatus, FieldType, RoleEnum

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    organization_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class TokenData(BaseModel):
    email: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    tenant_id: Optional[int] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    tenant_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Tenant Schemas
class TenantCreate(BaseModel):
    name: str
    slug: str

class TenantUpdate(BaseModel):
    name: Optional[str] = None

class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Role Schemas
class RoleResponse(BaseModel):
    id: int
    name: RoleEnum
    description: Optional[str]
    permissions: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class UserRoleAssign(BaseModel):
    user_id: int
    role_id: int

# Subscription Schemas
class SubscriptionCreate(BaseModel):
    tenant_id: int
    tier: SubscriptionTier = SubscriptionTier.FREE
    max_pages_per_month: int = 100

class SubscriptionUpdate(BaseModel):
    tier: Optional[SubscriptionTier] = None
    max_pages_per_month: Optional[int] = None
    is_active: Optional[bool] = None

class SubscriptionResponse(BaseModel):
    id: int
    tenant_id: int
    tier: SubscriptionTier
    max_pages_per_month: int
    current_month_usage: int
    is_active: bool
    starts_at: datetime
    
    class Config:
        from_attributes = True

# Form Schema Schemas
class FormFieldCreate(BaseModel):
    field_name: str
    field_label: str
    field_type: FieldType
    is_required: bool = False
    default_value: Optional[str] = None
    regex_validation: Optional[str] = None
    dropdown_options: Optional[List[str]] = None
    cross_field_rules: Optional[Dict[str, Any]] = None
    field_group: Optional[str] = None
    display_order: int = 0

class FormFieldResponse(FormFieldCreate):
    id: int
    schema_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class FormSchemaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    fields: List[FormFieldCreate]

class FormSchemaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class FormSchemaResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    description: Optional[str]
    version: int
    is_active: bool
    created_at: datetime
    fields: List[FormFieldResponse]
    
    class Config:
        from_attributes = True

# Document Schemas
class DocumentUploadResponse(BaseModel):
    id: int
    original_filename: str
    file_path: str
    status: DocumentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    tenant_id: int
    form_schema_id: Optional[int]
    original_filename: str
    num_pages: int
    status: DocumentStatus
    overall_confidence: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FieldValueResponse(BaseModel):
    id: int
    field_id: int
    field_name: str
    extracted_value: Optional[str]
    normalized_value: Optional[str]
    confidence_score: float
    needs_review: bool
    final_value: Optional[str]
    
    class Config:
        from_attributes = True

# System Config Schemas
class SystemConfigCreate(BaseModel):
    config_key: str
    config_value: Dict[str, Any]
    description: Optional[str] = None
    is_secret: bool = False

class SystemConfigUpdate(BaseModel):
    config_value: Dict[str, Any]
    description: Optional[str] = None

class SystemConfigResponse(BaseModel):
    id: int
    config_key: str
    config_value: Dict[str, Any]
    description: Optional[str]
    is_secret: bool
    updated_at: datetime
    
    class Config:
        from_attributes = True