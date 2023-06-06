from typing import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud.user_post import mark_posts_as_read
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
    assert len(resp.json()) == 3
    assert resp.json()[0]["uuid"] == str(posts[2].uuid)  # most recent
    assert resp.json()[1]["uuid"] == str(posts[1].uuid)
    assert resp.json()[2]["uuid"] == str(posts[0].uuid)


def test_list_all_posts_read(
    client: TestClient,
    db: Session,
    user_bob: User,
    feed_science: Feed,
    url_list_posts: Callable,
) -> None:
    user = user_bob

    # User didn't mark any post as read yet
    assert user.read_posts.count() == 0

    # Mark post 1 and 2 as read
    posts = feed_science.posts.all()[:2]
    mark_posts_as_read(db, user_bob, posts)

    assert user.read_posts.count() == 2

    url = url_list_posts(user_uuid=user.uuid, read="true")
    resp = client.get(url)

    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert resp.json()[0]["uuid"] == str(posts[1].uuid)  # most recent
    assert resp.json()[1]["uuid"] == str(posts[0].uuid)


def test_list_all_posts_unread(
    client: TestClient,
    db: Session,
    user_bob: User,
    feed_science: Feed,
    url_list_posts: Callable,
) -> None:
    user = user_bob

    # User didn't mark any post as read yet
    assert user.read_posts.count() == 0

    # Mark post 1 read
    post_1 = feed_science.posts.filter_by(title="[Science] Post 1").one()
    mark_posts_as_read(db, user_bob, [post_1])

    assert user.read_posts.count() == 1

    url = url_list_posts(user_uuid=user.uuid, read="false")
    resp = client.get(url)

    posts = feed_science.posts.all()

    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert resp.json()[0]["uuid"] == str(posts[2].uuid)  # most recent
    assert resp.json()[1]["uuid"] == str(posts[1].uuid)


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
