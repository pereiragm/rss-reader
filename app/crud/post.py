from sqlalchemy.orm import Session

from app.models import Post
from app.schemas.post import PostCreate


def create_post(db: Session, obj_in: PostCreate, feed_id: int) -> Post:
    post_obj = Post(feed_id=feed_id, **obj_in.dict())
    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    return post_obj
