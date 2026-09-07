from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from klip.db import get_db
from klip.api.deps import get_current_user
from klip.schemas import SnippetRead, SnippetCreate, SnippetListRead
from klip.models import User
from klip.services import (
    create_snippet,
    fetch_snippet,
    list_of_snippets,
    delete_snippet,
)
from klip.exceptions import (
    ExpiredSnippet,
    PrivateSnippet,
    SnippetNotFound,
    SnippetForbidden,
)
from klip.core import settings


router = APIRouter(prefix="/snippet", tags=["snippets"])


@router.post("", response_model=SnippetRead, status_code=201)
def Snippet_create(
    snippet_data: SnippetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_snippet(snippet_data, db, current_user)


@router.get("/fetch/{public_id}", response_model=SnippetRead)
def Snippet_by_id(
    public_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return fetch_snippet(public_id, db, current_user)
    except (ExpiredSnippet, PrivateSnippet, SnippetNotFound) as e:
        raise HTTPException(status_code=404, detail="Not Found") from e


@router.get("/snippetlist", response_model=SnippetListRead)
def user_snippets(
    limit: int = Query(
        default=settings.default_page_size, le=settings.max_page_size, ge=1
    ),
    cursor: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return list_of_snippets(db, current_user, limit, cursor)
    except SnippetNotFound as e:
        raise HTTPException(status_code=404,detail="No Snippets") from e


@router.delete("/{public_id}", status_code=204)
def snippet_delete(
    public_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return delete_snippet(public_id, current_user, db)
    except (SnippetForbidden, SnippetNotFound) as e:
        if e == SnippetForbidden:
            raise HTTPException(status_code=403, details="Forbidden")

        if e == SnippetNotFound:
            raise HTTPException(status_code=404, details="NotFound")
