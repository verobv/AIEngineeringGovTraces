from pydantic import BaseModel, Field
from typing import Literal

class GovernanceFinding(BaseModel):
    """
    Structured feedback from a Critic. 
    Using Pydantic ensures we get parsable JSON, not random text.
    """

    # Chain-of-Thought
    critic: Literal[
        "Anomaly",
        "Safety",
        "Policy",
        "Reasoning",
        "Integrity"
    ]

    severity: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Risk score assigned by the critic."
    )

    finding: str = Field(
        ...,
        description="Short explanation of the detected issue."
    )

    evidence: str = Field(
        ...,
        description="Trace evidence supporting the finding."
    )

class GovernanceAssessment(BaseModel):
    """
    The synthesis decision from the Chairman.
    """
    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    summary: str = Field(
        ...,
        description="Overall synthesis of all governance findings."
    )