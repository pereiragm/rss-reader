from uuid import UUID

from app.api.v1.exceptions import FeedNotFound, UserNotFound
from app.api.v1.resources.base import BaseResourceApiV1
from app.crud.user_feed import subscribe_to_feeds, unsubscribe_from_feeds
from app.models import Feed


class SubscriptionResource(BaseResourceApiV1):
    def __init__(self, feeds_uuids: set[UUID], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feeds_uuids = feeds_uuids

    def _get_requested_feeds(self) -> list[Feed]:
        req_feeds = self.db.query(Feed).filter(Feed.uuid.in_(self.feeds_uuids)).all()

        # Check if all requested feeds uuids exist
        feeds_not_found = self.feeds_uuids - set([f.uuid for f in req_feeds])
        if feeds_not_found:
            raise FeedNotFound(f"UUIDs {feeds_not_found} not found")

        return req_feeds

    def follow_feeds(self) -> list[Feed]:
        if not self.user:
            raise UserNotFound("User UUID not found.")

        req_feeds = self._get_requested_feeds()

        # Select feeds to follow
        following_feeds = self.user.feeds.filter(Feed.uuid.in_(self.feeds_uuids)).all()
        feeds_to_follow_uuids = self.feeds_uuids - {f.uuid for f in following_feeds}
        if feeds_to_follow_uuids:
            feeds_to_follow = [f for f in req_feeds if f.uuid in feeds_to_follow_uuids]
            subscribe_to_feeds(self.db, user=self.user, feeds=feeds_to_follow)

        return self.user.feeds.all()

    def unfollow_feeds(self):
        if not self.user:
            raise UserNotFound("User UUID not found.")

        req_feeds = self._get_requested_feeds()

        # Select feeds to unfollow
        following_feeds = self.user.feeds.filter(Feed.uuid.in_(self.feeds_uuids)).all()
        feeds_to_unfollow_uuids = self.feeds_uuids.intersection(
            {f.uuid for f in following_feeds}
        )
        if feeds_to_unfollow_uuids:
            feeds_to_unfollow = [f for f in req_feeds if
                                 f.uuid in feeds_to_unfollow_uuids]
            unsubscribe_from_feeds(self.db, user=self.user, feeds=feeds_to_unfollow)

        return self.user.feeds.all()
