from fastapi import APIRouter, status

from app.deps import CurrentUser, SessionDep
from app.models import ProfileCreate, ProfileRead, ProfileUpdate, UserProfile

router = APIRouter(tags=["users"])


@router.post("/users", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
def create_user(data: ProfileCreate, session: SessionDep) -> UserProfile:
    user = UserProfile.model_validate(data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me/profile", response_model=ProfileRead)
def read_profile(user: CurrentUser) -> UserProfile:
    return user


@router.put("/me/profile", response_model=ProfileRead)
def update_profile(data: ProfileUpdate, user: CurrentUser, session: SessionDep) -> UserProfile:
    user.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
