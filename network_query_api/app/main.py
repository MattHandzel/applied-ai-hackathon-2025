from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from .database import Neo4jDatabase
from .query_processor import QueryProcessor
from .models import QueryRequest, QueryResponse, PersonCreate, RelationshipCreate

load_dotenv()

app = FastAPI(title="Network Query API", description="Natural language querying for social networks")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

db = Neo4jDatabase()
query_processor = QueryProcessor()

@app.on_event("startup")
async def startup_event():
    await db.connect()
    await db.create_sample_data()

@app.on_event("shutdown")
async def shutdown_event():
    await db.close()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
async def natural_language_query(request: QueryRequest):
    try:
        cypher_query = await query_processor.generate_cypher(request.query, request.user_name)
        
        results = await db.execute_query(cypher_query)
        
        return QueryResponse(
            query=request.query,
            results=results,
            cypher_used=cypher_query,
            execution_time="0.12s"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/person")
async def add_person(person: PersonCreate):
    try:
        result = await db.create_person(person)
        return {"message": "Person created successfully", "person": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/relationship")
async def add_relationship(rel: RelationshipCreate):
    try:
        result = await db.create_relationship(rel)
        return {"message": "Relationship created successfully", "relationship": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/stats")
async def get_graph_stats():
    try:
        stats = await db.get_graph_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
