from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Tenant, Subscription, UserRole as UserRoleModel, Role, RoleEnum, SubscriptionTier
from schemas import UserRegister, UserLogin, Token, UserResponse
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from datetime import timedelta
import os
from dotenv import load_dotenv
import re

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create tenant (organization)
    tenant_slug = slugify(user_data.organization_name)
    
    # Check if tenant slug exists
    base_slug = tenant_slug
    counter = 1
    while db.query(Tenant).filter(Tenant.slug == tenant_slug).first():
        tenant_slug = f"{base_slug}-{counter}"
        counter += 1
    
    tenant = Tenant(
        name=user_data.organization_name,
        slug=tenant_slug
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    # Create subscription (Free tier by default)
    subscription = Subscription(
        tenant_id=tenant.id,
        tier=SubscriptionTier.FREE,
        max_pages_per_month=100
    )
    db.add(subscription)
    db.commit()
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        tenant_id=tenant.id,
        is_active=True,
        is_verified=True  # Auto-verify for MVP
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign Admin role to first user of tenant
    admin_role = db.query(Role).filter(Role.name == RoleEnum.ADMIN).first()
    if admin_role:
        user_role = UserRoleModel(user_id=user.id, role_id=admin_role.id)
        db.add(user_role)
        db.commit()
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "tenant_id": user.tenant_id,
            "tenant_name": tenant.name,
            "is_active": user.is_active
        }
    }

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Get tenant info
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "tenant_id": user.tenant_id,
            "tenant_name": tenant.name if tenant else None,
            "is_active": user.is_active
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user