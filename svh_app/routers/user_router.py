from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.user_manager import UserManager
from schemas.user_schema import UserParser
from parsers.user_parser import UserCreate

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserParser.to_response)
def create_user(user: UserCreate, db: Session = Depends(get_db_session)):
    try:
        return UserManager(db).create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db_session)):
    return UserManager(db).list_users()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db_session)):
    u = UserManager(db).get_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, updates: dict, db: Session = Depends(get_db_session)):
    u = UserManager(db).update_user(user_id, updates)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db_session)):
    ok = UserManager(db).delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
