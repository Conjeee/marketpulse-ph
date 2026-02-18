from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class Ticker(str, Enum):
    """
    The PSEi 30 Stock
    """
    AC = "AC.PS"
    ACEN = "ACEN.PS"
    AEV = "AEV.PS"
    AGI = "AGI.PS"
    ALI = "ALI.PS"
    AP = "AP.PS"
    BDO = "BDO.PS"
    BLOOM = "BLOOM.PS"
    BPI = "BPI.PS"
    CNPF = "CNPF.PS"
    DMC = "DMC.PS"
    EMI = "EMI.PS"
    GLO = "GLO.PS"
    GTCAP = "GTCAP.PS"
    ICT = "ICT.PS"
    JFC = "JFC.PS"
    JGS = "JGS.PS"
    LTG = "LTG.PS"
    MBT = "MBT.PS"
    MER = "MER.PS"
    MONDE = "MONDE.PS"
    NIKL = "NIKL.PS"
    PGOLD = "PGOLD.PS"
    SCC = "SCC.PS"
    SM = "SM.PS"
    SMC = "SMC.PS"
    SMPH = "SMPH.PS"
    TEL = "TEL.PS"
    URC = "URC.PS"
    WLCON = "WLCON.PS"


class SentimentData(BaseModel):
    score: int = Field(
        ...,
        ge=-100,
        le=100,
        description="Sentiment score from -100 to 100"
    )
    label: str = Field(
        ...,
        pattern="^(Positive|Negative|Neutral)$"
    )
    reasoning: str


class MarketData(BaseModel):
    ticker: Ticker
    price: float = Field(
        ...,
        gt=0,
        le=100,
        description="Price must be positive"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    news_headline: Optional[str] = None
    sentiment: Optional[SentimentData] = None

    @field_validator('price')
    @classmethod
    def round_price(cls, v:float) -> float:
        return round(v, 4)