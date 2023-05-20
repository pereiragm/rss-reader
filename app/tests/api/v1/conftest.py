from datetime import datetime
from typing import Callable

import pytest
from sqlalchemy.orm import Session

from app.crud.crud_user import create_user
from app.crud.feed import create_feed
from app.crud.post import create_post
from app.models import Feed, User
from app.schemas.feed import FeedCreate
from app.schemas.post import PostCreate
from app.schemas.user import UserCreate


@pytest.fixture(scope="function")
def user_bob(db: Session) -> User:
    # Create user
    user_schema = UserCreate(name="Bob Smith", email="bob@email.com")
    return create_user(db, user_schema)


@pytest.fixture(scope="function")
def feed_science(db: Session) -> Feed:
    feed_science_schema = FeedCreate(
        title="Believe in Science",
        description="We talk about science.",
        link="http://sciencetoday.com",
        language="en",
        last_build_date=datetime.utcnow(),
    )
    feed = create_feed(db, feed_science_schema)

    posts_schemas = [
        PostCreate(
            title="[Science] Post 1",
            description="This is Post 1 about science",
            link="http://sciencetoday.com/posts/1",
            pub_date=datetime.utcnow(),
        ),
        PostCreate(
            title="[Science] Post 2",
            description="This is Post 2 about science",
            link="http://sciencetoday.com/posts/2",
            pub_date=datetime.utcnow(),
        ),
    ]
    for ps in posts_schemas:
        create_post(db, ps, feed_id=feed.id)

    return feed


@pytest.fixture(scope="function")
def feed_arts(db: Session) -> Feed:
    feed_arts_schema = FeedCreate(
        title="Life with Arts",
        description="We talk about arts.",
        link="http://arts.com",
        language="en",
        last_build_date=datetime.utcnow(),
    )
    return create_feed(db, feed_arts_schema)


@pytest.fixture(scope="function")
def feed_math(db: Session) -> Feed:
    feed_math_schema = FeedCreate(
        title="Believe in Math",
        description="We talk about math.",
        link="http://mathnow.com",
        language="en",
        last_build_date=datetime.utcnow(),
    )
    return create_feed(db, feed_math_schema)


#
@pytest.fixture(scope="function")
def url_follow_feed(*args, **kwargs) -> Callable:
    def f(*args, **kwargs):
        return f"/api/v1/users/{kwargs['user_uuid']}/feeds-follow"

    return f


@pytest.fixture(scope="function")
def url_unfollow_feed(*args, **kwargs) -> Callable:
    def f(*args, **kwargs):
        return f"/api/v1/users/{kwargs['user_uuid']}/feeds-unfollow"

    return f


@pytest.fixture(scope="function")
def url_read_posts(*args, **kwargs) -> Callable:
    def f(*args, **kwargs):
        return f"/api/v1/users/{kwargs['user_uuid']}/posts-read"

    return f


@pytest.fixture(scope="function")
def url_unread_posts(*args, **kwargs) -> Callable:
    def f(*args, **kwargs):
        return f"/api/v1/users/{kwargs['user_uuid']}/posts-unread"

    return f


@pytest.fixture(scope="function")
def url_refresh_feed(*args, **kwargs) -> Callable:
    def f(*args, **kwargs):
        return f"/api/v1/users/{kwargs['user_uuid']}/feeds/{kwargs['feed_uuid']}/refresh"

    return f
