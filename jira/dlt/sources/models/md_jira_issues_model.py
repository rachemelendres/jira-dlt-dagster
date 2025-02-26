from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import datetime
from typing import Optional

class MdJiraIssuesModel(BaseModel):
    id: str = Field(...)
    self: str = Field(...)
    key: str = Field(...)
    changelog: dict = Field(...)
    fields: dict = Field(...)
    updated: datetime = Field(...)
    created: datetime = Field(...)
    customer_id: Optional[str] = Field(None)
    partition_date: str = Field(...)
    
    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Validates that the `customer_id` is not empty"""
        if v:
            return v
        else:
            key = info.data.get('key')
            raise ValueError(f"`{key}` contains an empty {info.field_name}")