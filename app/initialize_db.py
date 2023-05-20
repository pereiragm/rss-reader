from app.crud.crud_user import create_user
from app.crud.feed import create_feed
from app.db.session import SessionLocal
from app.schemas.feed import FeedCreate
from app.schemas.user import UserCreate


def _create_feeds(db):
    feeds_info = [
        {
            "uuid": "1aea4dda-af96-4d0a-a1ed-0606457f9f53",
            "title": "NU - Algemeen",
            "description": "Het laatste nieuws het eerst op NU.nl",
            "link": "https://www.nu.nl/rss/Algemeen",
        },
        {
            "uuid": "a19ada88-f1c4-4633-b6bd-8776d2aa9680",
            "title": "Tweakers",
            "description": "Tweakers is de grootste hardwaresite en techcommunity van Nederland.",
            "link": "https://feeds.feedburner.com/tweakers/mixed",
        }
    ]

    for data in feeds_info:
        feed_in = FeedCreate(**data)
        create_feed(db, feed_in)


def _create_user(db):
    users_info = [
        UserCreate(
            name="Admin User",
            email="admin@test.com",
            uuid="220840cf-43fe-458f-8eb5-4e57fc5c8b23"
        ),
    ]
    for user_schema in users_info:
        create_user(db, user_schema)


def initialize_db():
    db = SessionLocal()
    try:
        _create_feeds(db)
        _create_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully.")
