from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, UUID4
from sqlalchemy.orm import Session

from app.crud.crud_user import get_user
from app.crud.user_feed import subscribe_to_feeds, unsubscribe_from_feeds
from app.deps import get_db
from app.models import Feed

router = APIRouter()


class FollowUnfollowRequestSchema(BaseModel):
    feeds: set[UUID4] = Field(title="List of feed UUIDs to be followed.")


class FeedSimple(BaseModel):
    uuid: UUID4
    title: str
    description: str
    link: str
    language: str | None = None
    last_build_date: datetime = None

    class Config:
        orm_mode = True


class FollowUnfollowRespSchema(BaseModel):
    feeds: list[FeedSimple]


@router.post("/users/{user_uuid}/feeds-follow", response_model=FollowUnfollowRespSchema)
async def follow_feeds(
    user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
    req_model: FollowUnfollowRequestSchema,
    db: Session = Depends(get_db),
):
    """
    Subscribe a user in multiple feeds.
    """
    user = get_user(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail=f"User UUID not found.")

    req_feeds_uuids = req_model.feeds

    # Check if all requested feeds uuids exist
    req_feeds = db.query(Feed).filter(Feed.uuid.in_(req_feeds_uuids)).all()
    feeds_not_found = req_feeds_uuids - set([f.uuid for f in req_feeds])
    if feeds_not_found:
        raise HTTPException(
            status_code=400, detail=f"UUIDs {feeds_not_found} not found"
        )

    # Select feeds to follow
    following_feeds = user.feeds.filter(Feed.uuid.in_(req_feeds_uuids)).all()
    feeds_to_follow_uuids = req_feeds_uuids - {f.uuid for f in following_feeds}
    if feeds_to_follow_uuids:
        feeds_to_follow = [f for f in req_feeds if f.uuid in feeds_to_follow_uuids]
        subscribe_to_feeds(db, user=user, feeds=feeds_to_follow)

    return {"feeds": user.feeds.all()}


@router.post(
    "/users/{user_uuid}/feeds-unfollow", response_model=FollowUnfollowRespSchema
)
async def unfollow_feeds(
    user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
    req_model: FollowUnfollowRequestSchema,
    db: Session = Depends(get_db),
):
    """
    Unsubscribe a user from multiple feeds.
    """
    user = get_user(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail=f"User UUID not found.")

    req_feeds_uuids = req_model.feeds

    # Check if all requested feeds uuids exist
    req_feeds = db.query(Feed).filter(Feed.uuid.in_(req_feeds_uuids)).all()
    feeds_not_found = req_feeds_uuids - set([f.uuid for f in req_feeds])
    if feeds_not_found:
        raise HTTPException(
            status_code=400, detail=f"UUIDs {feeds_not_found} not found"
        )

    # Select feeds to unfollow
    following_feeds = user.feeds.filter(Feed.uuid.in_(req_feeds_uuids)).all()
    feeds_to_unfollow_uuids = req_feeds_uuids.intersection(
        {f.uuid for f in following_feeds}
    )
    if feeds_to_unfollow_uuids:
        feeds_to_unfollow = [f for f in req_feeds if f.uuid in feeds_to_unfollow_uuids]
        unsubscribe_from_feeds(db, user=user, feeds=feeds_to_unfollow)

    return {"feeds": user.feeds.all()}
