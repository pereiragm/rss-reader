from typing import Callable

from fastapi.testclient import TestClient

from app.models import Feed, User


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
