from uuid import UUID

from app.api.v1.exceptions import PostNotFound, UserNotFound
from app.api.v1.resources.base import BaseResourceApiV1
from app.crud.user_post import mark_posts_as_read
from app.models import Post


class ReadUnreadPostsResource(BaseResourceApiV1):
    def __init__(self, posts_uuids: set[UUID], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.posts_uuids = posts_uuids

    def _get_requested_posts(self) -> list[Post]:
        req_posts = self.db.query(Post).filter(Post.uuid.in_(self.posts_uuids)).all()

        # Check if all requested posts uuids exist
        posts_not_found = self.posts_uuids - set([f.uuid for f in req_posts])
        if posts_not_found:
            raise PostNotFound(f"UUIDs {posts_not_found} not found")

        return req_posts

    def read_posts(self) -> list[Post]:
        if not self.user:
            raise UserNotFound("User UUID not found.")

        req_posts = self._get_requested_posts()

        # Select Posts to mark as read
        read_posts = self.user.read_posts.filter(Post.uuid.in_(self.posts_uuids)).all()
        posts_to_read_uuids = self.posts_uuids - {f.uuid for f in read_posts}
        if posts_to_read_uuids:
            posts_to_read = [p for p in req_posts if p.uuid in posts_to_read_uuids]
            mark_posts_as_read(self.db, user=self.user, posts=posts_to_read)

        return self.user.read_posts.all()
