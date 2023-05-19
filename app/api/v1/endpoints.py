from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path
from pydantic import BaseModel, Field, UUID4
from sqlalchemy.orm import Session

from app.crud.crud_user import get_user
from app.deps import get_db
from app.models import Feed

router = APIRouter()

"""
Request:
{
    feeds: [
        "feed_uuid1",
        "feed_uuid2",
        ...
    ]
}
Response:
{
    feeds: [
        {
            uuid: "uuid1",
            title
            description
        }   
    ]
}
"""


class FeedsFollowRequestModel(BaseModel):
    feeds: set[UUID4] = Field(title="List of feed UUIDs to be followed by the user.")


class FeedSimple(BaseModel):
    uuid: UUID4
    title: str
    description: str
    link: str
    language: str | None = None
    last_build_date: datetime = None


class FeedsFollowResponseModel(BaseModel):
    feeds: list[FeedSimple]


@router.post("/users/{user_uuid}/feeds-follow")
async def subscribe_to_feeds(
        user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
        req_model: FeedsFollowRequestModel,
        db: Session = Depends(get_db),
):
    user = get_user(db, user_uuid)
    req_feeds = req_model.feeds

    # Check if all requested feeds uuids exist
    feeds = set(db.query(Feed.uuid).filter(Feed.uuid.in_(req_feeds)).all())
    feeds_not_found = req_feeds - feeds
    if feeds_not_found:
        raise Exception("Feeds not found on the DB.")

    # query feeds followed by the user
    import pdb; pdb.set_trace()
    following = {f.uuid for f in user.feeds.filter(Feed.uuid.in_(req_feeds)).all()}

    feeds_to_follow = req_feeds - req_feeds.intersection(following)

    user.subscribe_to_feeds(db, feeds_to_follow)

    return {"feeds": req_model}
