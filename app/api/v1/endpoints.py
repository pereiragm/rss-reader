from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, UUID4
from sqlalchemy.orm import Session

from app.api.v1.exceptions import FeedNotFound, PostNotFound, UserNotFound
from app.api.v1.resources.auth import AuthenticationError, LoginResource
from app.api.v1.resources.list_posts import PostsResource
from app.api.v1.resources.read_unread import ReadUnreadPostsResource
from app.api.v1.resources.refresh_feed import RefreshFeedNotFound, RefreshFeedResource
from app.api.v1.resources.subscription import SubscriptionResource
from app.core.security import SCOPES
from app.deps import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/token",
    scopes=SCOPES
)


class FollowUnfollowRequestSchema(BaseModel):
    feeds: set[UUID4] = Field(title="List of feeds UUIDs.")


class ReadUnreadPostsRequestSchema(BaseModel):
    posts: set[UUID4] = Field(title="List of posts UUIDs.")


class PostsRequestSchema(BaseModel):
    read: bool = Field(title="Read indicator.")
    feed_uuid: UUID4 = Field(title="Feed UUID.")


class FeedSimple(BaseModel):
    uuid: UUID4
    title: str
    description: str
    link: str
    language: str | None = None
    last_build_date: datetime = None

    class Config:
        orm_mode = True


class PostSimple(BaseModel):
    uuid: UUID4
    title: str
    description: str
    link: str
    pub_date: datetime

    class Config:
        orm_mode = True


class FollowUnfollowRespSchema(BaseModel):
    feeds: list[FeedSimple]


class ReadUnreadPostsRespSchema(BaseModel):
    posts: list[PostSimple]


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db),
):
    resource = LoginResource(
        db=db,
        username=form_data.username,
        password=form_data.password,
        requested_scopes=form_data.scopes
    )

    try:
        token = resource.authenticate()
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.args[0])

    return token


@router.post("/users/{user_uuid}/feeds-follow", response_model=FollowUnfollowRespSchema)
async def follow_feeds(
        user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
        req_model: FollowUnfollowRequestSchema,
        db: Session = Depends(get_db),
):
    """
    Subscribe a user in multiple feeds.
    """
    resource = SubscriptionResource(
        db=db, user_uuid=user_uuid, feeds_uuids=req_model.feeds
    )

    try:
        feeds = resource.follow_feeds()
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
    except FeedNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])

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

    resource = SubscriptionResource(
        db=db, user_uuid=user_uuid, feeds_uuids=req_model.feeds
    )

    try:
        feeds = resource.unfollow_feeds()
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
    except FeedNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])

    return {"feeds": feeds}


@router.post("/users/{user_uuid}/posts-read", response_model=ReadUnreadPostsRespSchema)
async def read_posts(
        user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
        req_model: ReadUnreadPostsRequestSchema,
        db: Session = Depends(get_db),
):
    """
    Mark posts as read.
    """
    resource = ReadUnreadPostsResource(
        db=db, user_uuid=user_uuid, posts_uuids=req_model.posts
    )

    try:
        posts = resource.read_posts()
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
    except PostNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])

    return {"posts": posts}


@router.post(
    "/users/{user_uuid}/posts-unread", response_model=ReadUnreadPostsRespSchema
)
async def unread_posts(
        user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
        req_model: ReadUnreadPostsRequestSchema,
        db: Session = Depends(get_db),
):
    """
    Mark posts as unread.
    """
    resource = ReadUnreadPostsResource(
        db=db, user_uuid=user_uuid, posts_uuids=req_model.posts
    )

    try:
        posts = resource.unread_posts()
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
    except PostNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])

    return {"posts": posts}


@router.get("/users/{user_uuid}/posts", response_model=list[PostSimple])
async def list_posts(
        user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
        read: bool | None = None,
        feed_uuid: UUID | None = None,
        db: Session = Depends(get_db),
):
    """
    List posts according to filters (by feed, by read/unread)
    """
    resource = PostsResource(db=db, user_uuid=user_uuid, read=read, feed_uuid=feed_uuid)

    try:
        posts = resource.get_posts()
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=e.args[0])

    return posts


@router.get("/users/{user_uuid}/feeds/{feed_uuid}/refresh")
async def refresh_feed(
        user_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
        feed_uuid: Annotated[UUID, Path(title="Must be a valid UUID")],
        db: Session = Depends(get_db),
):
    """
    Force a feed refresh.
    """
    resource = RefreshFeedResource(db=db, user_uuid=user_uuid, feed_uuid=feed_uuid)
    try:
        resource.refresh()
    except (UserNotFound, RefreshFeedNotFound) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])

    return {"message": f"Feed {feed_uuid} has been refreshed successfully."}
