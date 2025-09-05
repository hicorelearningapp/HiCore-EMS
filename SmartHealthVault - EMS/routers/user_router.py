from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.user_model import User
from services.user_service import UserService
from database import get_db

router = APIRouter()

def _service(db=Depends(get_db)):
    return UserService(db.users)

@router.post("/", response_model=User)
def create_user(user: User, svc: UserService = Depends(_service)):
    created = svc.create_user(user)
    return created

@router.get("/", response_model=List[User])
def list_users(svc: UserService = Depends(_service)):
    return svc.list_users()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: str, svc: UserService = Depends(_service)):
    u = svc.get_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

@router.patch("/{user_id}", response_model=User)
def update_user(user_id: str, payload: dict, svc: UserService = Depends(_service)):
    u = svc.update_user(user_id, payload)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

@router.delete("/{user_id}")
def delete_user(user_id: str, svc: UserService = Depends(_service)):
    deleted = svc.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Deleted"}
