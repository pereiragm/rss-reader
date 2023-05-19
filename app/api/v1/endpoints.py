from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, UUID4
from sqlalchemy.orm import Session

from app.api.v1.exceptions import FeedNotFound, UserNotFound
from app.api.v1.resources.subscription import SubscriptionResource
from app.deps import get_db

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
    resource = SubscriptionResource(db=db, user_uuid=user_uuid,
                                    feeds_uuids=req_model.feeds)

    try:
        feeds = resource.follow_feeds()
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=e.args[0])
    except FeedNotFound as e:
        raise HTTPException(status_code=400, detail=e.args[0])

    return {"feeds": feeds}


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

    resource = SubscriptionResource(db=db, user_uuid=user_uuid,
                                    feeds_uuids=req_model.feeds)

    try:
        feeds = resource.unfollow_feeds()
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=e.args[0])
    except FeedNotFound as e:
        raise HTTPException(status_code=400, detail=e.args[0])

    return {"feeds": feeds}
