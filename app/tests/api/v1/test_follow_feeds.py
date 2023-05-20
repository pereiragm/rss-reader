from typing import Callable

from fastapi.testclient import TestClient

from app.models import Feed, User


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
