from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.api.v1 import api_router
from app.crud import crud_user
from app.deps import get_db
from app.schemas import user

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")


@app.post("/users/", response_model=user.User)
def create_user(user_in: user.UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user_in)
