from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud.crud_user import create_user
from app.crud.feed import create_feed_v2
from app.schemas.feed import FeedCreate
from app.schemas.user import UserCreate


def test_user_follow_feeds(client: TestClient, db: Session) -> None:
    # Create user
    user_model = UserCreate(name="Bob Smith", email="bob@email.com")
    user = create_user(db, user_model)

    # Create feeds
    feed_science_model = FeedCreate(
        title="Believe in Science",
        description="We talk about science.",
        link="http://sciencetoday.com",
        language="en",
        last_build_date=datetime.utcnow()
    )
    feed_math_model = FeedCreate(
        title="Believe in Math",
        description="We talk about math.",
        link="http://mathnow.com",
        language="en",
        last_build_date=datetime.utcnow()
    )
    feed_science = create_feed_v2(db, feed_science_model)
    feed_math = create_feed_v2(db, feed_math_model)

    # does not follow any feed yet
    assert user.feeds.count() == 0

    url = f"/api/v1/users/{str(user.uuid)}/feeds-follow"
    data = {
        "feeds": [
            str(feed_science.uuid),
            str(feed_math.uuid),
        ]
    }
    r = client.post(url, json=data)

    following_feeds = user.feeds.all()
    assert r.status_code == 200
    assert following_feeds[0] == feed_science
    assert following_feeds[1] == feed_math

