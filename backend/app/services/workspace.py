from app.models.workspace import Workspace
from app.services.crud import CRUDBase

workspace_service = CRUDBase(Workspace)
