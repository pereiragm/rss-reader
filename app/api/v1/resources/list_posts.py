from uuid import UUID

from sqlalchemy import desc

from app.api.v1.exceptions import UserNotFound
from app.api.v1.resources.base import BaseResourceApiV1
from app.models import Feed
from app.models import Post


class PostsResource(BaseResourceApiV1):
    def __init__(self, read: bool | None, feed_uuid: UUID | None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read = read
        self.feed_uuid = feed_uuid

    def _get_filtered_posts(self) -> list[Post]:
        req_posts = None

        # evaluating filter to get posts
        if self.feed_uuid is None:
            # get posts of all feeds

            if self.read is None:
                # get posts read and unread
                # Must implement pagination
                req_posts = self.db.query(Post).order_by(desc(Post.pub_date)).all()

            else:
                if self.read:
                    req_posts = self.user.read_posts.order_by(
                        Post.pub_date.desc()
                    ).all()

                else:
                    # get unread posts
                    read_posts = self.user.read_posts.subquery()
                    req_posts = (
                        self.db.query(Post)
                        .filter(Post.id.notin_(self.db.query(read_posts.c.id)))
                        .order_by(Post.pub_date.desc())
                        .all()
                    )

        else:
            # get posts of just one feed followed by user

            feed = self.db.query(Feed).filter(Feed.uuid == self.feed_uuid)

            if self.read is None:
                # get posts read and unread of the feed
                req_posts = (
                    self.db.query(Post)
                    .order_by(desc(Post.pub_date))
                    .filter(Post.feed_id == feed.id)
                    .all()
                )

            else:
                if self.read:
                    # get posts read of the feed
                    read_posts = self.user.read_posts.filter(self.user.id)
                    req_posts = [p for p in read_posts if p.feed_id == feed.id]

                else:
                    # get posts unread of the feed
                    all_posts_of_feed = (
                        self.db.query(Post)
                        .order_by(desc(Post.pub_date))
                        .filter(Post.feed_id == feed.id)
                        .all()
                    )
                    read_posts = self.user.read_posts.filter(self.user.id)
                    req_posts = [
                        p for p in all_posts_of_feed if not (p.uuid in read_posts)
                    ]

        # returning list of posts
        return req_posts

    def get_posts(self) -> list[Post]:
        if not self.user:
            raise UserNotFound("User UUID not found.")

        posts = self._get_filtered_posts()

        return posts
