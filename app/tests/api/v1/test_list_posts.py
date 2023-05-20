from typing import Callable

import pytest
from fastapi.testclient import TestClient

from app.models import Feed, User


def test_list_posts_common(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_list_posts: Callable,
) -> None:
    user = user_bob

    # User didn't mark any post as read yet
    assert user.read_posts.count() == 0

    url = url_list_posts(user_uuid=user.uuid)
    resp = client.get(url)

    posts = feed_science.posts.all()

    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert resp.json()[0]["uuid"] == str(posts[1].uuid)  # most recent
    assert resp.json()[1]["uuid"] == str(posts[0].uuid)


@pytest.mark.xfail(reason="Not implemented yet.")
def test_list_all_posts_read(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_list_posts: Callable,
) -> None:
    assert False


@pytest.mark.xfail(reason="Not implemented yet.")
def test_list_all_posts_unread(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_list_posts: Callable,
) -> None:
    assert False


@pytest.mark.xfail(reason="Not implemented yet.")
def test_list_all_posts_of_feed(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_list_posts: Callable,
) -> None:
    assert False


@pytest.mark.xfail(reason="Not implemented yet.")
def test_list_read_posts_of_feed(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_list_posts: Callable,
) -> None:
    assert False


@pytest.mark.xfail(reason="Not implemented yet.")
def test_list_unread_posts_of_feed(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_list_posts: Callable,
) -> None:
    assert False
