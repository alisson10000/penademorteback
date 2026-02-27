from app.core.database import Base

# Importa models aqui para o Base.metadata enxergar
from app.modules.survey.models import User, Question, Answer  # noqa: F401
from app.modules.admin.models import Admin  # noqa: F401