from typing import Dict, List

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from fastapi import FastAPI, HTTPException, Form, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from flowers_repository import FlowersRepository
from users_repository import UsersRepository
from models import User, Flower, UserRequest, FlowerRequest
from database import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)
app = FastAPI()

flowers_repository = FlowersRepository()
users_repository = UsersRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
shopping_cart = []


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_jwt(id: int) -> str:
    body = {"id": id}
    token = jwt.encode(body, "BadBreacking", "HS256")
    return token


def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "BadBreacking", "HS256")
    return data["id"]


@app.post("/signup", status_code=200)
def post_signup(user: UserRequest, db: Session = Depends(get_db)):
    try:
        new_user = User(email=user.email, full_name=user.full_name, password=user.password)
        users_repository.save(db, new_user)
    except KeyError:
        raise HTTPException(status_code=400, detail="User already exists")

    return {"message": "User registered successfully"}


@app.post("/login", status_code=200, response_model=Dict[str, str])
def post_login(form_data: OAuth2PasswordRequestForm = Depends(),
               db: Session = Depends(get_db)):
    user_db = users_repository.get_user_by_email(db, form_data.username)
    if user_db is None or user_db.password != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_jwt(user_db.id)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/profile", status_code=200, response_model=UserRequest)
def get_profile(token: str = Depends(oauth2_scheme),
                db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    user_db = users_repository.get_user_by_id(db, user_id)
    print(user_db.email)
    new_user = UserRequest(id=user_id, email=user_db.email, full_name=user_db.full_name, password=user_db.password)
    if new_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    new_user.password = None
    return new_user


@app.get("/flowers", status_code=200, response_model=List[FlowerRequest])
def get_flowers(token: str = Depends(oauth2_scheme),
                db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    user = users_repository.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    flowers = flowers_repository.get_all(db)
    return flowers


@app.post("/flowers")
def post_flowers(flower: FlowerRequest, db: Session = Depends(get_db)):
    try:
        new_flower = Flower(name=flower.name, count=flower.count, cost=flower.cost)
        flowers_repository.save(db, new_flower)
    except KeyError:
        raise HTTPException(status_code=400, detail="Flower already exists")

    return {"message": "Flower registered successfully"
            }


@app.patch("/flowers/{flower_id}")
def patch_flowers(flower_id: int, update_flower: FlowerRequest, db: Session = Depends(get_db)):
    try:
        new_data = Flower(name=update_flower.name, cost=update_flower.cost, count=update_flower.count)
        flowers_repository.update(db, new_data, flower_id)
        return {"message": "User updated successfully"}
    except:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/flowers/{flower_id}")
def delete_flowers(flower_id: int, db: Session = Depends(get_db)):
    try:
        flowers_repository.delete(db, flower_id)
        return {"message": "Flower deleted successfully",
                "flower_id": flower_id
                }
    except:
        raise HTTPException(status_code=404, detail="User not found")



@app.post("/cart/items", status_code=200)
def add_to_cart(flower_id: int = Form()):
    shopping_cart.append(flower_id)
    response = JSONResponse(content={"message": "Item added to cart successfully"}, status_code=200)
    response.set_cookie(key="cart_items", value=",".join(map(str, shopping_cart)))
    return response


@app.get("/cart/items")
def get_to_cart(request: Request, db: Session = Depends(get_db)):
    cart_items = request.cookies.get("cart_items")
    cart_flowers = []
    total_price = 0.0

    if cart_items:
        cart_items_list = list(map(int, cart_items.split(",")))
        for flower_id in cart_items_list:
            flower = flowers_repository.get_by_id(db, flower_id)
            if flower:
                cart_flowers.append(flower)
                total_price += flower.cost
    return {
        "cart_flowers": cart_flowers,
        "total_price": total_price
    }
