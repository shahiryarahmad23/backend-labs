from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_, delete
import secrets
from datetime import datetime, UTC
from klip.schemas import SnippetCreate, SnippetRead, SnippetListRead
from klip.models import User, SnippetTable, VisibleValue, UserRole
from klip.exceptions import (
    ExpiredSnippet,
    PrivateSnippet,
    SnippetNotFound,
    SnippetForbidden,
)
from klip.core import cursor_decode, cursor_encode


def create_snippet(snippet_data: SnippetCreate, db: Session, current_user: User):

    public = secrets.token_urlsafe(32)

    snippet = SnippetTable(
        owner_id=current_user.id,
        title=snippet_data.title,
        public_id=public,
        body=snippet_data.body,
        visibility=snippet_data.visibility,
        expires_at=snippet_data.expires_at,
    )

    db.add(snippet)
    db.commit()
    db.refresh(snippet)

    return snippet


def fetch_snippet(public_id: str, db: Session, current_user: User):

    snippet = db.execute(
        select(SnippetTable).where(SnippetTable.public_id == public_id)
    ).scalar_one_or_none()

    if snippet == None:
        raise SnippetNotFound("Snippet does not exit")

    if snippet.expires_at < datetime.now(UTC):
        raise ExpiredSnippet("Snippet is expired")

    if snippet.visibility == VisibleValue.PUBLIC:
        return snippet

    if snippet.visibility == VisibleValue.UNLISTED:
        return snippet

    if (
        snippet.visibility == VisibleValue.PRIVATE
        and current_user is not None
        and current_user.id == snippet.owner_id
    ):
        return snippet

    raise PrivateSnippet("The snippet is private")


def list_of_snippets(
    db: Session, current_user: User, limit: int, cursor: str | None = None
):

    stmt = (
        select(SnippetTable)
        .where(SnippetTable.owner_id == current_user.id)
        .order_by(
            SnippetTable.created_at.desc(),
            SnippetTable.id.desc(),
        )
        .limit(limit + 1)
    )

    if cursor:
        created_at, id = cursor_decode(cursor)
        stmt = stmt.where(
            or_(
                SnippetTable.created_at < created_at,
                and_(SnippetTable.created_at == created_at, SnippetTable.id < id),
            )
        )

    snippets = db.execute(stmt).scalars().all()

    if not snippets:
        raise SnippetNotFound("There are no snippet of the user")

    has_next_page = len(snippets) > limit

    if has_next_page:
        snippets = snippets[:limit]

    next_cursor = None

    if has_next_page:
        last_created_at = snippets[-1].created_at
        last_id = snippets[-1].id
        next_cursor = cursor_encode(last_created_at, last_id)

    return SnippetListRead(snippets=snippets, cursor=next_cursor)


def delete_snippet(public_id: str,current_user: User, db: Session):
    
    snippet = db.execute(select(SnippetTable).where(SnippetTable.public_id == public_id)).scalar_one_or_none()
    
    if snippet is None:
        raise SnippetNotFound("No Snippet")
    
    if current_user.role == UserRole.PRIVILEGED:
        db.delete(snippet)
    elif current_user.role == UserRole.OWNER:
        if snippet.owner_id != current_user.id:
            raise SnippetForbidden("Fobidden")
        db.delete(snippet)
    db.commit()
        
    return None
        
        
