from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.project import Project
from app.models.prompt import Prompt
from app.models.session import Session
from app.models.workspace import Workspace

router = APIRouter(tags=["search"])


class SearchResult(BaseModel):
    type: str
    id: str
    name: str
    breadcrumb: str
    match: str


@router.get("/search", response_model=list[SearchResult])
async def search(q: str = "", session: AsyncSession = Depends(get_session)):
    if not q or len(q.strip()) == 0:
        return []

    keyword = f"%{q}%"

    results: list[SearchResult] = []

    # Workspaces
    stmt = select(Workspace).where(
        or_(Workspace.name.ilike(keyword), Workspace.description.ilike(keyword))
    ).limit(20)
    for ws in (await session.execute(stmt)).scalars().all():
        results.append(SearchResult(
            type="workspace", id=ws.id, name=ws.name,
            breadcrumb=ws.name,
            match=ws.name if keyword[1:-1].lower() in ws.name.lower() else (ws.description or "")[:100],
        ))

    # Projects
    stmt = select(Project).where(
        or_(Project.name.ilike(keyword), Project.description.ilike(keyword))
    ).limit(20)
    for proj in (await session.execute(stmt)).scalars().all():
        ws = await session.get(Workspace, proj.workspace_id)
        results.append(SearchResult(
            type="project", id=proj.id, name=proj.name,
            breadcrumb=f"{ws.name}/{proj.name}" if ws else proj.name,
            match=proj.name if keyword[1:-1].lower() in proj.name.lower() else (proj.description or "")[:100],
        ))

    # Sessions
    stmt = select(Session).where(
        or_(Session.name.ilike(keyword), Session.description.ilike(keyword))
    ).limit(20)
    for sess in (await session.execute(stmt)).scalars().all():
        proj = await session.get(Project, sess.project_id)
        ws = await session.get(Workspace, proj.workspace_id) if proj else None
        results.append(SearchResult(
            type="session", id=sess.id, name=sess.name,
            breadcrumb=f"{ws and ws.name}/{proj and proj.name}/{sess.name}",
            match=sess.name if keyword[1:-1].lower() in sess.name.lower() else (sess.description or "")[:100],
        ))

    # Prompts
    stmt = select(Prompt).where(
        or_(Prompt.name.ilike(keyword), Prompt.system_prompt.ilike(keyword), Prompt.user_prompt.ilike(keyword))
    ).limit(20)
    for prompt in (await session.execute(stmt)).scalars().all():
        sess = await session.get(Session, prompt.session_id)
        proj = await session.get(Project, sess.project_id) if sess else None
        ws = await session.get(Workspace, proj.workspace_id) if proj else None
        results.append(SearchResult(
            type="prompt", id=prompt.id, name=prompt.name,
            breadcrumb=f"{ws and ws.name}/{proj and proj.name}/{sess and sess.name}/{prompt.name}",
            match=prompt.name if keyword[1:-1].lower() in prompt.name.lower() else (prompt.system_prompt or prompt.user_prompt or "")[:100],
        ))

    return results
