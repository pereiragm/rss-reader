from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from rss_reader.crud import crud_user
from rss_reader.db.session import SessionLocal
from rss_reader.schemas import user

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/users/", response_model=user.User)
def create_user(user_in: user.UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user_in)
