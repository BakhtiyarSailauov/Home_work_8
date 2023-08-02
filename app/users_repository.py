from typing import List

from models import User, UserRequest
from sqlalchemy.orm import Session


class UsersRepository:
    def save(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_user_by_email(self, db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db:Session, id: int) -> User:
        return db.query(User).filter(User.id == id).first()

    def get_users(self, db: Session) -> List[User]:
        return db.query(User).all()