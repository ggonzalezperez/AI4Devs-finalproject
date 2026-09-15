from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_child, get_current_family_user
from app.models.child import Child
from app.models.family import User
from app.repositories import story as story_repo
from app.schemas.story import StoryRead, StoryReview
from app.services import story_service

router = APIRouter(tags=["stories"])


# ---- Niño ----

@router.post("/me/stories", response_model=StoryRead, status_code=status.HTTP_201_CREATED)
def create_my_story(
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> StoryRead:
    story = story_service.create_story(db, child)
    return StoryRead.model_validate(story)


@router.get("/me/stories", response_model=list[StoryRead])
def my_stories(
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> list[StoryRead]:
    stories = story_repo.list_for_child(db, child.id, status="approved")
    return [StoryRead.model_validate(s) for s in stories]


@router.get("/me/stories/{story_id}", response_model=StoryRead)
def my_story(
    story_id: int,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> StoryRead:
    story = story_repo.get_for_child(db, child.id, story_id)
    if story is None or story.status != "approved":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuento no encontrado")
    return StoryRead.model_validate(story)


# ---- Familia ----

@router.get("/family/stories", response_model=list[StoryRead])
def family_stories(
    status_filter: str | None = None,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> list[StoryRead]:
    stories = story_repo.list_for_family(db, user.family_id, status=status_filter)
    return [StoryRead.model_validate(s) for s in stories]


@router.put("/family/stories/{story_id}", response_model=StoryRead)
def review_family_story(
    story_id: int,
    payload: StoryReview,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> StoryRead:
    story = story_repo.get_for_family(db, user.family_id, story_id)
    if story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuento no encontrado")
    story = story_service.review_story(db, story, payload.action, payload.title, payload.body)
    return StoryRead.model_validate(story)
