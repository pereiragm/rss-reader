from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path
from pydantic import BaseModel, Field, UUID4
from sqlalchemy.orm import Session

from app.crud.crud_user import get_user
from app.crud.user_feed import subscribe_user_to_feeds
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


@router.post("/users/{user_uuid}/feeds-follow", response_model=FeedsFollowResponseModel)
async def subscribe_to_feeds(
        user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
        req_model: FeedsFollowRequestModel,
        db: Session = Depends(get_db),
):
    """
    - Get all feeds from the requested uuids
    - Check if all requested uuids exist on the DB
        - False -> return 400
    - Select feeds that the user does not follow
    - Add subscription for them
    """

    user = get_user(db, user_uuid)
    req_feeds_uuids = req_model.feeds

    # Check if all requested feeds uuids exist
    req_feeds = db.query(Feed).filter(Feed.uuid.in_(req_feeds_uuids)).all()
    feeds_not_found = req_feeds_uuids - set([f.uuid for f in req_feeds])
    if feeds_not_found:
        raise Exception("Feeds not found on the DB.")

    # Select feeds to follow
    following_feeds = user.feeds.filter(Feed.uuid.in_(req_feeds_uuids)).all()
    feeds_to_follow_uuids = req_feeds_uuids - {f.uuid for f in following_feeds}
    feeds_to_follow = [f for f in req_feeds if f.uuid in feeds_to_follow_uuids]

    subscribe_user_to_feeds(db, user=user, feeds=feeds_to_follow)

    return {"feeds": user.feeds.all()}
