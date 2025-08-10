from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str
    user_name: str = "CurrentUser"

class QueryResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    cypher_used: str
    execution_time: str

class PersonCreate(BaseModel):
    name: str
    age: Optional[int] = None
    bio: Optional[str] = None

class RelationshipCreate(BaseModel):
    from_person: str
    to_person: str
    relationship_type: str
    properties: Optional[Dict[str, Any]] = {}

class LocationCreate(BaseModel):
    city: str
    country: str

class OrganizationCreate(BaseModel):
    name: str
    type: str
    industry: Optional[str] = None

class InterestCreate(BaseModel):
    name: str
    category: Optional[str] = None

class SkillCreate(BaseModel):
    name: str
    level: Optional[str] = None
