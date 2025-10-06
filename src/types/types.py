from typing import Optional
from utils.enums import Position, Modality, Website, JobType

class JobBase:
    title: str
    company: str
    url: str
    published_at: str
    position: Position
    website: Website
    modality: Optional[Modality]
    location: Optional[str]
    description: Optional[str]
    salary: Optional[str]
    type_: Optional[JobType]
    remote: Optional[bool]
