from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_child
from app.models.child import Child
from app.repositories import knowledge as knowledge_repo
from app.schemas.knowledge import ChildProfile, KnowledgeNodeRead, Suggestion
from app.services import child_service, me_suggestions

router = APIRouter(prefix="/me", tags=["me"])



@router.get("/knowledge", response_model=list[KnowledgeNodeRead])
def my_knowledge(
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> list[KnowledgeNodeRead]:
    return [
        KnowledgeNodeRead.model_validate(n) for n in knowledge_repo.list_for_child(db, child.id)
    ]


@router.get("/suggestions", response_model=list[Suggestion])
def my_suggestions(child: Child = Depends(get_current_child)) -> list[Suggestion]:
    return [Suggestion(**s) for s in me_suggestions.sample()]


@router.get("/profile", response_model=ChildProfile)
def my_profile(
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> ChildProfile:
    return child_service.build_profile(db, child)
