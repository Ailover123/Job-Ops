from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class CollectorSourceBase(BaseModel):
    company_name: str
    source_type: str = Field(pattern="^(greenhouse|lever)$")
    board_token: Optional[str] = None
    company_id: Optional[str] = None
    enabled: bool = True

class CollectorSourceCreate(CollectorSourceBase):
    @model_validator(mode='after')
    def check_identifiers(self):
        if self.source_type == 'greenhouse' and not self.board_token:
            raise ValueError('board_token is required for greenhouse source_type')
        if self.source_type == 'lever' and not self.company_id:
            raise ValueError('company_id is required for lever source_type')
        return self

class CollectorSourceUpdate(BaseModel):
    company_name: Optional[str] = None
    source_type: Optional[str] = Field(default=None, pattern="^(greenhouse|lever)$")
    board_token: Optional[str] = None
    company_id: Optional[str] = None
    enabled: Optional[bool] = None

class CollectorSourceResponse(CollectorSourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_error: Optional[str] = None
    last_fetched_count: Optional[int] = None
    last_saved_count: Optional[int] = None

    class Config:
        from_attributes = True
