"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session

from app.db import get_session
from app.models import UserProfile

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    session: SessionDep,
    x_user_id: Annotated[int | None, Header()] = None,
) -> UserProfile:
    """Return the user making the request.

    TODO(auth): for now the client sends its user id in the `X-User-Id` header.
    Later this reads a token instead; routes using this dependency stay unchanged.
    """
    if x_user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing X-User-Id header")
    user = session.get(UserProfile, x_user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


CurrentUser = Annotated[UserProfile, Depends(get_current_user)]
