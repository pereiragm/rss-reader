from sqlalchemy.orm import Session

from app.models import Post

from app.schemas.post import PostBase, PostCreate


def get_most_recent_post_by_feed(db: Session, feed_id: int) -> Post:
    return (
        db.query(Post)
        .filter(Post.feed_id == feed_id)
        .order_by(Post.pub_date.desc())
        .one()
    )


def create_post(db: Session, obj_in: PostBase, feed_id: int) -> Post:
    post_obj = Post(
        feed_id=feed_id,
        title=obj_in.title,
        description=obj_in.description,
        link=obj_in.link,
        pub_date=obj_in.pub_date,
    )
    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    return post_obj


def create_post_v2(db: Session, obj_in: PostCreate, feed_id: int) -> Post:
    post_obj = Post(feed_id=feed_id, **obj_in.dict())
    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    return post_obj
