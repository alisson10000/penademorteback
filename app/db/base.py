from app.core.database import Base

# Importa models aqui para o Base.metadata enxergar todas as tabelas
from app.modules.admin.models import Admin  # noqa: F401
from app.modules.survey.models import User, Question, Answer  # noqa: F401
from app.modules.ads.models import Ad  # noqa: F401
