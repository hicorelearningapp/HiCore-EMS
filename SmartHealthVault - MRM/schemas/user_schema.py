from models.user_model import UserModel
from parsers.user_parser import UserCreate, UserResponse
from passlib.hash import bcrypt
from datetime import datetime

class UserParser:
    @staticmethod
    def parse_create(payload: UserCreate) -> UserModel:
        # The validation is now handled by Pydantic v2
        return UserModel(
            name=payload.name,
            email=payload.email,
            password_hash=bcrypt.hash(payload.password),
            gender=payload.gender,
            age=payload.age,
            dob=payload.dob,  # Already validated by Pydantic
            blood_group=payload.blood_group,
            address=payload.address,
            role=payload.role
        )

    @staticmethod
    def to_response(model: UserModel) -> UserResponse:
        # Convert SQLAlchemy model to Pydantic model
        return UserResponse.model_validate({
            'id': str(model.id),
            'name': model.name,
            'email': model.email,
            'gender': model.gender,
            'age': model.age,
            'dob': model.dob,
            'blood_group': model.blood_group,
            'address': model.address,
            'role': model.role or 'patient'
        })
