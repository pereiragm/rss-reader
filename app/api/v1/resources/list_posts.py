from uuid import UUID

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
        if self.feed_uuid is None:
            # get posts of all feeds
            base_q = self.db.query(Post)

            if self.read is None:
                # get all posts
                req_posts_q = base_q
            else:
                read_posts_q = self.user.read_posts.subquery()

                if self.read:
                    # get read posts
                    req_posts_q = base_q.filter(
                        Post.id.in_(self.db.query(read_posts_q.c.id))
                    )
                else:
                    req_posts_q = base_q.filter(
                        Post.id.notin_(self.db.query(read_posts_q.c.id))
                    )
        else:
            # get posts of just one feed
            base_q = (
                self.db.query(Post)
                .join(Feed, Feed.id == Post.feed_id)
                .filter(Feed.uuid == self.feed_uuid)
            )

            if self.read is None:
                # get all posts of a specific feed
                req_posts_q = base_q
            else:
                read_posts_q = self.user.read_posts.subquery()
                if self.read:
                    # get read posts of the feed
                    req_posts_q = base_q.filter(
                        Post.id.in_(self.db.query(read_posts_q.c.id))
                    )
                else:
                    # get unread posts of the feed
                    req_posts_q = base_q.filter(
                        Post.id.notin_(self.db.query(read_posts_q.c.id))
                    )

        # TODO: implement pagination
        return req_posts_q.order_by(Post.pub_date.desc()).all()

    def get_posts(self) -> list[Post]:
        if not self.user:
            raise UserNotFound("User UUID not found.")

        posts = self._get_filtered_posts()

        return posts
