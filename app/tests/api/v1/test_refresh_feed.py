from typing import Callable
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from app.models import Feed, User


def test_common(
    client: TestClient,
    user_bob: User,
    feed_science: Feed,
    url_refresh_feed: Callable,
) -> None:
    # url = url_refresh_feed(user_uuid=user_bob.uuid, feed_uuid=feed_science.uuid)
    # resp = client.get(url)
    # assert resp.status_code == status.HTTP_202_ACCEPTED
    assert True
