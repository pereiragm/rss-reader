from datetime import datetime
from typing import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud.crud_user import create_user
from app.crud.feed import create_feed_v2
from app.models import Feed, User
from app.schemas.feed import FeedCreate
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
    return create_feed_v2(db, feed_science_schema)


@pytest.fixture(scope="function")
def feed_arts(db: Session) -> Feed:
    feed_arts_schema = FeedCreate(
        title="Life with Arts",
        description="We talk about arts.",
        link="http://arts.com",
        language="en",
        last_build_date=datetime.utcnow(),
    )
    return create_feed_v2(db, feed_arts_schema)


@pytest.fixture(scope="function")
def feed_math(db: Session) -> Feed:
    feed_math_schema = FeedCreate(
        title="Believe in Math",
        description="We talk about math.",
        link="http://mathnow.com",
        language="en",
        last_build_date=datetime.utcnow(),
    )
    return create_feed_v2(db, feed_math_schema)


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


def test_follow_feeds_common(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    feed_math: Feed,
    url_follow_feed: Callable,
) -> None:
    user = user_bob

    # User does not follow any feed yet
    assert user.feeds.count() == 0

    url = url_follow_feed(user_uuid=user.uuid)
    data = {
        "feeds": [
            str(feed_science.uuid),
            str(feed_math.uuid),
        ]
    }

    resp = client.post(url, json=data)

    following_feeds = user.feeds.all()
    assert resp.status_code == 200
    assert following_feeds[0] == feed_science
    assert following_feeds[1] == feed_math
    assert resp.json()["feeds"][0]["uuid"] == str(feed_science.uuid)


def test_follow_feeds_with_nonexistent_feed_uuid(
    client: TestClient, user_bob: User, feed_math: Feed, url_follow_feed: Callable
) -> None:
    user = user_bob
    nonexistent_uuid = "9431c184-57d2-4a96-898c-81e622aab43b"
    url = url_follow_feed(user_uuid=user.uuid)
    data = {
        "feeds": [
            nonexistent_uuid,
            str(feed_math.uuid),
        ]
    }
    resp = client.post(url, json=data)
    assert resp.status_code == 400
    assert (
        resp.json()["detail"]
        == "UUIDs {UUID('9431c184-57d2-4a96-898c-81e622aab43b')} not found"
    )


def test_follow_feeds_user_not_found(
    client: TestClient,
    user_bob: User,
    feed_math: Feed,
    feed_science: Feed,
    url_follow_feed: Callable,
) -> None:
    nonexistent_uuid = "090e7626-7e98-4a92-bafb-8fa132f8e779"
    url = url_follow_feed(user_uuid=nonexistent_uuid)
    data = {"feeds": [str(feed_science.uuid)]}
    resp = client.post(url, json=data)
    assert resp.status_code == 404


def test_follow_feeds_already_following_some_feeds(
    client: TestClient,
    user_bob: User,
    feed_math: Feed,
    feed_science: Feed,
    feed_arts: Feed,
    url_follow_feed: Callable,
) -> None:
    user = user_bob
    url = url_follow_feed(user_uuid=user.uuid)

    assert user.feeds.count() == 0

    data = {
        "feeds": [
            str(feed_science.uuid),
            str(feed_math.uuid),
        ]
    }
    resp = client.post(url, json=data)

    # User follows science and math feeds
    assert resp.status_code == 200
    assert user.feeds.count() == 2
    assert len(resp.json()["feeds"]) == 2

    # Requesting to follow arts (and science and math again)
    data = {
        "feeds": [
            str(feed_science.uuid),
            str(feed_math.uuid),
            str(feed_arts.uuid),
        ]
    }
    resp = client.post(url, json=data)

    assert resp.status_code == 200
    assert user.feeds.count() == 3
    assert len(resp.json()["feeds"]) == 3


def test_unfollow_feeds_common(
    client: TestClient,
    user_bob: User,
    feed_math: Feed,
    feed_science: Feed,
    feed_arts: Feed,
    url_follow_feed: Callable,
    url_unfollow_feed: Callable,
) -> None:
    user = user_bob

    assert user.feeds.count() == 0

    # User follows science, math and arts
    url_follow = url_follow_feed(user_uuid=user.uuid)
    data = {
        "feeds": [
            str(feed_science.uuid),
            str(feed_math.uuid),
            str(feed_arts.uuid),
        ]
    }
    resp = client.post(url_follow, json=data)

    assert user.feeds.count() == 3

    # Unfollow science and math
    url_unfollow = url_unfollow_feed(user_uuid=user.uuid)
    data = {
        "feeds": [
            str(feed_science.uuid),
            str(feed_math.uuid),
        ]
    }
    resp = client.post(url_unfollow, json=data)

    assert resp.status_code == 200
    assert user.feeds.one() == feed_arts
    assert resp.json()["feeds"][0]["uuid"] == str(feed_arts.uuid)


def test_unfollow_feeds_with_nonexistent_feed_uuid(
    client: TestClient, user_bob: User, feed_math: Feed, url_unfollow_feed: Callable
) -> None:
    user = user_bob
    nonexistent_uuid = "9431c184-57d2-4a96-898c-81e622aab43b"
    url = url_unfollow_feed(user_uuid=user.uuid)
    data = {
        "feeds": [
            nonexistent_uuid,
            str(feed_math.uuid),
        ]
    }
    resp = client.post(url, json=data)
    assert resp.status_code == 400
    assert (
        resp.json()["detail"]
        == "UUIDs {UUID('9431c184-57d2-4a96-898c-81e622aab43b')} not found"
    )


def test_unfollow_feeds_user_not_found(
    client: TestClient,
    user_bob: User,
    feed_math: Feed,
    feed_science: Feed,
    url_unfollow_feed: Callable,
) -> None:
    nonexistent_uuid = "090e7626-7e98-4a92-bafb-8fa132f8e779"
    url = url_unfollow_feed(user_uuid=nonexistent_uuid)
    data = {"feeds": [str(feed_science.uuid)]}
    resp = client.post(url, json=data)
    assert resp.status_code == 404


def test_unfollow_feeds_that_user_does_not_follow(
    client: TestClient,
    user_bob: User,
    feed_math: Feed,
    feed_science: Feed,
    feed_arts: Feed,
    url_follow_feed: Callable,
    url_unfollow_feed: Callable,
) -> None:
    user = user_bob

    # User follows science
    url_follow = url_follow_feed(user_uuid=user.uuid)
    resp = client.post(url_follow, json={"feeds": [str(feed_science.uuid)]})

    assert user.feeds.one() == feed_science

    # Unfollow math and arts (does not take any effect)
    url_unfollow = url_unfollow_feed(user_uuid=user.uuid)
    data = {
        "feeds": [
            str(feed_math.uuid),
            str(feed_arts.uuid),
        ]
    }
    resp = client.post(url_unfollow, json=data)

    assert resp.status_code == 200
    assert user.feeds.one() == feed_science
