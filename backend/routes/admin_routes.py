from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from models import User, SystemConfig, Tenant, Subscription, Document, AuditLog
from schemas import SystemConfigCreate, SystemConfigUpdate, SystemConfigResponse
from auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Helper function to check if user is admin
def is_admin(current_user: User, db: Session) -> bool:
    from models import UserRole as UserRoleModel, Role, RoleEnum
    user_roles = db.query(Role).join(UserRoleModel).filter(
        UserRoleModel.user_id == current_user.id,
        Role.name == RoleEnum.ADMIN
    ).first()
    return user_roles is not None

@router.get("/config", response_model=List[SystemConfigResponse])
async def list_system_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    configs = db.query(SystemConfig).all()
    return configs

@router.get("/config/{config_key}", response_model=SystemConfigResponse)
async def get_system_config(
    config_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    return config

@router.post("/config", response_model=SystemConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_system_config(
    config_data: SystemConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if config key exists
    existing = db.query(SystemConfig).filter(
        SystemConfig.config_key == config_data.config_key
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Config key already exists"
        )
    
    config = SystemConfig(
        config_key=config_data.config_key,
        config_value=config_data.config_value,
        description=config_data.description,
        is_secret=config_data.is_secret,
        updated_by=current_user.id
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config

@router.put("/config/{config_key}", response_model=SystemConfigResponse)
async def update_system_config(
    config_key: str,
    config_update: SystemConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    config.config_value = config_update.config_value
    if config_update.description is not None:
        config.description = config_update.description
    config.updated_by = current_user.id
    
    db.commit()
    db.refresh(config)
    
    return config

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    total_tenants = db.query(Tenant).count()
    total_users = db.query(User).count()
    total_documents = db.query(Document).count()
    
    # Count by subscription tier
    from models import SubscriptionTier
    free_tier = db.query(Subscription).filter(Subscription.tier == SubscriptionTier.FREE).count()
    standard_tier = db.query(Subscription).filter(Subscription.tier == SubscriptionTier.STANDARD).count()
    professional_tier = db.query(Subscription).filter(Subscription.tier == SubscriptionTier.PROFESSIONAL).count()
    
    # Count by document status
    from models import DocumentStatus
    uploaded = db.query(Document).filter(Document.status == DocumentStatus.UPLOADED).count()
    processing = db.query(Document).filter(Document.status == DocumentStatus.PROCESSING).count()
    completed = db.query(Document).filter(Document.status == DocumentStatus.COMPLETED).count()
    failed = db.query(Document).filter(Document.status == DocumentStatus.FAILED).count()
    
    return {
        "tenants": {
            "total": total_tenants
        },
        "users": {
            "total": total_users
        },
        "subscriptions": {
            "free": free_tier,
            "standard": standard_tier,
            "professional": professional_tier
        },
        "documents": {
            "total": total_documents,
            "uploaded": uploaded,
            "processing": processing,
            "completed": completed,
            "failed": failed
        }
    }

@router.get("/tenants")
async def list_all_tenants(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    
    result = []
    for tenant in tenants:
        subscription = db.query(Subscription).filter(
            Subscription.tenant_id == tenant.id
        ).first()
        
        result.append({
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "created_at": tenant.created_at,
            "subscription_tier": subscription.tier.value if subscription else None,
            "usage": subscription.current_month_usage if subscription else 0
        })
    
    return result