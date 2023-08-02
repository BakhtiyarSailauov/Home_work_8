from models import Flower, FlowerRequest
from typing import List

from sqlalchemy.orm import Session


class FlowersRepository:
    def get_all(self, db: Session) -> List[Flower]:
        return db.query(Flower).all()

    def save(self, db: Session, flower: Flower):
        flower.id = len(self.get_all(db)) + 1
        db.add(flower)
        db.commit()
        db.refresh(flower)
        return flower

    def get_by_id(self, db: Session, id: int) -> Flower:
        return db.query(Flower).filter(Flower.id == id).first()

    def delete(self, db: Session, flower_id: int):
        flower = db.query(Flower).filter(Flower.id == flower_id).first()
        db.delete(flower)
        db.commit()

    def update(self, db: Session, update_flower: Flower, flower_id: int):
        flower = db.query(Flower).filter(Flower.id == flower_id).first()
        flower.name = update_flower.name
        flower.cost = update_flower.cost
        flower.count = update_flower.count
        db.commit()
        db.refresh(flower)

