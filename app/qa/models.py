"""
Pydantic models for the QA / anomaly-detection layer.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class QAFinding(BaseModel):
    check_name: str
    severity: Severity
    message: str
    simulation_id: Optional[int] = None
    row_id: Optional[int] = None
    value: Optional[float] = None
    threshold: Optional[float] = None


class QAReport(BaseModel):
    simulation_id: Optional[int] = None
    rows_checked: int
    findings: list[QAFinding]
    passed: bool  # True if no CRITICAL findings