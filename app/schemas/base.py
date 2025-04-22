from pydantic import BaseModel
from pydantic import ConfigDict

class BaseModelWithConfig(BaseModel):
    """Базовая модель с включённой конфигурацией для работы с ORM"""
    model_config = ConfigDict(from_attributes=True)
