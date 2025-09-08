# parsers/user_parser.py
from models.user_model import UserModel
from schemas.user_schema import UserCreate, UserResponse
from passlib.hash import bcrypt

class UserParser:
    @staticmethod
    def parse_create(payload: UserCreate) -> UserModel:
        return UserModel(
            name=payload.name,
            email=payload.email,
            password_hash=bcrypt.hash(payload.password),
            gender=payload.gender,
            age=payload.age,
            dob=payload.dob
        )

    @staticmethod
    def to_response(model: UserModel) -> UserResponse:
        return UserResponse.from_orm(model)
