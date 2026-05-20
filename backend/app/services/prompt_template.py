from app.models.prompt_template import PromptTemplate
from app.services.crud import CRUDBase

prompt_template_service = CRUDBase(PromptTemplate)
