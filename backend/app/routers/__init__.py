from app.debug.router import router as debug_router
from app.routers.execution import router as execution_router
from app.routers.files import router as files_router
from app.routers.health import router as health_router
from app.routers.patterns import router as patterns_router
from app.routers.projects import router as projects_router
from app.routers.prompts import router as prompts_router
from app.routers.providers import router as providers_router
from app.routers.sessions import router as sessions_router
from app.routers.templates import router as templates_router
from app.routers.tokenize import router as tokenize_router
from app.routers.workspaces import router as workspaces_router

routers = [
    health_router,
    patterns_router,
    providers_router,
    workspaces_router,
    projects_router,
    sessions_router,
    prompts_router,
    execution_router,
    files_router,
    templates_router,
    tokenize_router,
    debug_router,
]
