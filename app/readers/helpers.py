from datetime import datetime

from sqlalchemy.orm import Session

from app.crud.feed import get_feed
from app.crud.post import create_post
from app.models import Feed, Post
from app.readers.base_reader import RSSFeedReader
from app.readers.exceptions import FeedNotFound


def refresh_feed(db: Session, feed_uuid: str) -> None:
    def _get_most_recent_post_pub_date(_feed: Feed) -> datetime | None:
        post = _feed.posts.order_by(Post.pub_date.desc()).first()
        return post.pub_date if post else None

    feed = get_feed(db, feed_uuid)
    if not feed:
        raise FeedNotFound(f"Feed {feed_uuid} not found")

    most_recent_post_dt = _get_most_recent_post_pub_date(feed)
    reader = RSSFeedReader(rss_url=feed.link)

    if most_recent_post_dt is None:
        # Select all posts retrieved from the RSS feed
        posts_to_be_added = reader.model.posts
    else:
        posts_to_be_added = [
            post
            for post in reader.model.posts
            if post.pub_date > most_recent_post_dt
        ]

    for post in posts_to_be_added:
        create_post(db, obj_in=post, feed_id=feed.id)
