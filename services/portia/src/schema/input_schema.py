from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date

YEAR_MIN = 2010
YEAR_MAX = 2025

def _coerce_num(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace(",", "").strip()
    try:
        return float(s)
    except Exception:
        return None

def _valid_ymd(s: str) -> bool:
    try:
        y, m, d = map(int, s.split("-"))
        _ = date(y, m, d)
        return True
    except Exception:
        return False

class NormalizedInput(BaseModel):
    companyName: Optional[str] = None
    companyNumber: Optional[str] = None
    accountingYear: int = Field(..., ge=YEAR_MIN, le=YEAR_MAX)
    yearEnd: Optional[str] = None  # YYYY-MM-DD (optional)
    revenueGBP: float = Field(..., ge=0)
    expensesGBP: float = Field(..., ge=0)
    rAndDSpendGBP: Optional[float] = Field(default=0, ge=0)
    capexGBP: Optional[float] = Field(default=0, ge=0)
    patentRevenueGBP: Optional[float] = Field(default=0, ge=0)
    applyCredits: Optional[bool] = True

    @validator("yearEnd", always=True)
    def _default_year_end(cls, v, values):
        if v is None:
            y = values.get("accountingYear")
            if y:
                return f"{y}-12-31"
        if v and not _valid_ymd(v):
            raise ValueError("yearEnd must be YYYY-MM-DD")
        return v
