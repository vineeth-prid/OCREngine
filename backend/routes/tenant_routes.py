from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Tenant, Subscription
from schemas import TenantResponse, TenantUpdate, SubscriptionResponse
from auth import get_current_user

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])

@router.get("/me", response_model=TenantResponse)
async def get_my_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant

@router.put("/me", response_model=TenantResponse)
async def update_my_tenant(
    tenant_update: TenantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if tenant_update.name is not None:
        tenant.name = tenant_update.name
    
    db.commit()
    db.refresh(tenant)
    return tenant

@router.get("/me/subscription", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == current_user.tenant_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return subscription

@router.get("/me/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == current_user.tenant_id
    ).first()
    
    if not subscription:
        return {
            "current_month_usage": 0,
            "max_pages_per_month": 0,
            "percentage_used": 0
        }
    
    percentage = (subscription.current_month_usage / subscription.max_pages_per_month * 100) if subscription.max_pages_per_month > 0 else 0
    
    return {
        "current_month_usage": subscription.current_month_usage,
        "max_pages_per_month": subscription.max_pages_per_month,
        "percentage_used": round(percentage, 2),
        "tier": subscription.tier.value,
        "remaining_pages": max(0, subscription.max_pages_per_month - subscription.current_month_usage)
    }