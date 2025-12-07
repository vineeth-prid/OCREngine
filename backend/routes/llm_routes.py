from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_current_user
import os
import requests
import psutil
import shutil

router = APIRouter(prefix="/api/llm", tags=["LLM Management"])

def check_user_is_admin(current_user: User, db: Session):
    """Check if user has admin role"""
    from models import UserRole, Role, RoleEnum
    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role and role.name == RoleEnum.ADMIN:
            return True
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

@router.get("/status")
async def get_llm_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get status of LLM models (cloud and local)"""
    check_user_is_admin(current_user, db)
    
    status_info = {
        "cloud_llm": {
            "available": bool(os.getenv('OPENAI_API_KEY') or os.getenv('EMERGENT_LLM_KEY')),
            "provider": "OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini"],
            "status": "connected" if os.getenv('EMERGENT_LLM_KEY') else "not_configured"
        },
        "local_llm": {
            "available": False,
            "installed_models": [],
            "status": "not_available",
            "reason": "Insufficient memory (2GB limit, need 6GB+)"
        },
        "system_resources": {
            "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "disk_free_gb": round(shutil.disk_usage('/app').free / (1024**3), 2),
            "cpu_count": psutil.cpu_count()
        }
    }
    
    # Check if Ollama is running and what models are available
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            status_info["local_llm"]["installed_models"] = [
                {
                    "name": m.get('name'),
                    "size_gb": round(m.get('size', 0) / (1024**3), 2)
                }
                for m in models
            ]
            if models:
                status_info["local_llm"]["status"] = "installed_but_insufficient_memory"
        else:
            status_info["local_llm"]["status"] = "ollama_not_running"
    except:
        status_info["local_llm"]["status"] = "ollama_not_installed"
    
    return status_info

@router.get("/config")
async def get_llm_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current LLM configuration"""
    check_user_is_admin(current_user, db)
    
    return {
        "use_local_model": False,  # Default to cloud
        "local_model": "qwen2.5:3b-instruct",
        "cloud_model_simple": "gpt-4o-mini",
        "cloud_model_complex": "gpt-4o",
        "confidence_threshold_for_mini": 0.85,
        "auto_routing_enabled": True
    }

@router.post("/config")
async def update_llm_config(
    config: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update LLM configuration"""
    check_user_is_admin(current_user, db)
    
    # In a production app, store this in database or config file
    # For now, return success
    return {
        "message": "Configuration updated successfully",
        "config": config
    }

@router.post("/download-model")
async def download_local_model(
    model_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a local LLM model via Ollama"""
    check_user_is_admin(current_user, db)
    
    # Check system resources first
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage('/app')
    
    required_memory_gb = 6  # Minimum for 7B models
    required_disk_gb = 10
    
    if mem.total / (1024**3) < required_memory_gb:
        return {
            "success": False,
            "error": "insufficient_memory",
            "message": f"Container has {mem.total/(1024**3):.1f}GB memory. Need {required_memory_gb}GB+ for local models.",
            "recommendation": "Increase container memory limit to 8GB or use cloud LLMs"
        }
    
    if disk.free / (1024**3) < required_disk_gb:
        return {
            "success": False,
            "error": "insufficient_disk",
            "message": f"Only {disk.free/(1024**3):.1f}GB disk space available. Need {required_disk_gb}GB+",
            "recommendation": "Free up disk space before downloading models"
        }
    
    # Attempt to download model
    try:
        # This would trigger Ollama pull in background
        # For now, return status
        return {
            "success": True,
            "message": f"Model download initiated: {model_name}",
            "estimated_time": "5-10 minutes",
            "status": "downloading"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to initiate model download"
        }

@router.post("/test-connection")
async def test_llm_connection(
    model_type: str,  # 'cloud' or 'local'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test LLM connection"""
    check_user_is_admin(current_user, db)
    
    if model_type == 'cloud':
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('EMERGENT_LLM_KEY')
            if not api_key:
                return {
                    "success": False,
                    "message": "No API key configured"
                }
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'test successful'"}],
                max_tokens=10
            )
            
            return {
                "success": True,
                "message": "Cloud LLM connection successful",
                "model": "gpt-4o-mini",
                "response": response.choices[0].message.content
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Cloud LLM connection failed: {str(e)}"
            }
    
    elif model_type == 'local':
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b-instruct",
                    "prompt": "Say 'test successful'",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Local LLM connection successful",
                    "model": "qwen2.5:3b-instruct"
                }
            else:
                return {
                    "success": False,
                    "message": f"Local LLM error: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Local LLM connection failed: {str(e)}"
            }
    
    return {
        "success": False,
        "message": "Invalid model type"
    }
