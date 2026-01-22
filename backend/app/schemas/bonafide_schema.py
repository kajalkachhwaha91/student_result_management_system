from pydantic import BaseModel
from typing import Literal

class BonafideRequestSchema(BaseModel):
    reason: str

class BonafideApprovalSchema(BaseModel):
    status: Literal["APPROVED", "REJECTED"]
