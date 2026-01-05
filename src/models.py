from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Metadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    source_type: str  # web, pdf, wiki
    additional: Dict[str, str] = Field(default_factory=dict)

class Segment(BaseModel):
    type: str  # heading, text, image, table
    content: str
    metadata: Dict[str, str] = Field(default_factory=dict)

class Document(BaseModel):
    metadata: Metadata
    segments: List[Segment]
