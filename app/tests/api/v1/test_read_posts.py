from typing import Callable

from fastapi.testclient import TestClient

from app.models import Feed, User


def test_common(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_read_posts: Callable,
) -> None:
    user = user_bob

    # User didn't mark any post as read yet
    assert user.read_posts.count() == 0

    url = url_read_posts(user_uuid=user.uuid)
    data = {"posts": [str(feed_science.posts[0].uuid), str(feed_science.posts[1].uuid)]}
    resp = client.post(url, json=data)

    read_posts = user.read_posts.all()
    assert resp.status_code == 200
    assert len(read_posts) == 2
    assert read_posts[0] == feed_science.posts[0]
    assert read_posts[1] == feed_science.posts[1]
    assert resp.json()["posts"][0]["uuid"] == str(feed_science.posts[0].uuid)


def test_with_nonexistent_post_uuid(
    client: TestClient, user_bob: User, feed_science: Feed, url_read_posts: Callable
) -> None:
    user = user_bob
    nonexistent_uuid = "9431c184-57d2-4a96-898c-81e622aab43b"
    url = url_read_posts(user_uuid=user.uuid)
    data = {"posts": [nonexistent_uuid]}
    resp = client.post(url, json=data)
    assert resp.status_code == 400
    assert (
        resp.json()["detail"]
        == "UUIDs {UUID('9431c184-57d2-4a96-898c-81e622aab43b')} not found"
    )


def test_user_not_found(
    client: TestClient,
    feed_science: Feed,
    url_read_posts: Callable,
) -> None:
    nonexistent_uuid = "090e7626-7e98-4a92-bafb-8fa132f8e779"
    url = url_read_posts(user_uuid=nonexistent_uuid)
    data = {"posts": [str(feed_science.posts[0].uuid)]}
    resp = client.post(url, json=data)
    assert resp.status_code == 404


def test_already_read_posts(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_read_posts: Callable,
) -> None:
    user = user_bob
    url = url_read_posts(user_uuid=user.uuid)

    assert user.read_posts.count() == 0

    data = {"posts": [str(feed_science.posts[0].uuid)]}
    resp = client.post(url, json=data)

    # User read posts 1 from science
    assert resp.status_code == 200
    assert user.read_posts.count() == 1
    assert len(resp.json()["posts"]) == 1

    # Request to mark post 2 as read (and post 1)
    data = {"posts": [str(feed_science.posts[0].uuid), str(feed_science.posts[1].uuid)]}
    resp = client.post(url, json=data)

    assert resp.status_code == 200
    assert user.read_posts.count() == 2
    assert len(resp.json()["posts"]) == 2
