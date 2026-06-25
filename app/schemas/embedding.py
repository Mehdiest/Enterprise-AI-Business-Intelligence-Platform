"""
Embedding schemas.
"""

from pydantic import BaseModel


class SemanticSearchRequest(BaseModel):
    query: str


class SemanticSearchResponse(BaseModel):
    query: str
    result: str
    similarity_score: float