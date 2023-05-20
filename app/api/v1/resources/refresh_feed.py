from uuid import UUID

from app.api.v1.exceptions import UserNotFound
from app.api.v1.resources.base import BaseResourceApiV1
from app.readers.exceptions import FeedNotFound
from app.readers.helpers import refresh_feed


class RefreshFeedNotFound(Exception):
    pass


class RefreshFeedResource(BaseResourceApiV1):
    def __init__(self, feed_uuid: UUID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feed_uuid = feed_uuid

    def refresh(self):
        if not self.user:
            raise UserNotFound("User UUID not found.")

        try:
            refresh_feed(self.db, str(self.feed_uuid))
        except FeedNotFound as e:
            raise RefreshFeedNotFound(e.args[0])
