from neo4j import AsyncGraphDatabase
import os
from typing import List, Dict, Any, Optional
from .models import PersonCreate, RelationshipCreate

class Neo4jDatabase:
    def __init__(self):
        self.driver = None
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")

    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(
            self.uri, 
            auth=(self.user, self.password)
        )
        
        async with self.driver.session() as session:
            result = await session.run("RETURN 1 as test")
            await result.consume()
        print("Connected to Neo4j successfully")

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.driver:
            raise Exception("Database not connected")
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def create_person(self, person: PersonCreate) -> Dict[str, Any]:
        query = """
        CREATE (p:Person {name: $name, age: $age, bio: $bio})
        RETURN p
        """
        parameters = {
            "name": person.name,
            "age": person.age,
            "bio": person.bio
        }
        result = await self.execute_query(query, parameters)
        return result[0] if result else {}

    async def create_relationship(self, rel: RelationshipCreate) -> Dict[str, Any]:
        query = f"""
        MATCH (a:Person {{name: $from_person}})
        MATCH (b:Person {{name: $to_person}})
        CREATE (a)-[r:{rel.relationship_type} $properties]->(b)
        RETURN r
        """
        parameters = {
            "from_person": rel.from_person,
            "to_person": rel.to_person,
            "properties": rel.properties
        }
        result = await self.execute_query(query, parameters)
        return result[0] if result else {}

    async def get_graph_stats(self) -> Dict[str, Any]:
        queries = {
            "total_nodes": "MATCH (n) RETURN count(n) as count",
            "total_relationships": "MATCH ()-[r]->() RETURN count(r) as count",
            "person_count": "MATCH (p:Person) RETURN count(p) as count",
            "organization_count": "MATCH (o:Organization) RETURN count(o) as count"
        }
        
        stats = {}
        for key, query in queries.items():
            result = await self.execute_query(query)
            stats[key] = result[0]["count"] if result else 0
        
        return stats

    async def create_sample_data(self):
        sample_data_queries = [
            "CREATE (alice:Person {name: 'Alice', age: 25, bio: 'Software engineer, loves reading'})",
            "CREATE (bob:Person {name: 'Bob', age: 27, bio: 'Product manager with fintech experience'})",
            "CREATE (carol:Person {name: 'Carol', age: 24, bio: 'Cornell student, 3rd year CS'})",
            "CREATE (will:Person {name: 'Will', age: 26, bio: 'Lives in SF, into rock climbing'})",
            "CREATE (currentuser:Person {name: 'CurrentUser', age: 28, bio: 'The main user of the system'})",
            
            "CREATE (sf:Location {city: 'San Francisco', country: 'USA'})",
            "CREATE (ny:Location {city: 'New York', country: 'USA'})",
            
            "CREATE (stripe:Organization {name: 'Stripe', type: 'Company', industry: 'Fintech'})",
            "CREATE (cornell:Organization {name: 'Cornell', type: 'University', industry: 'Education'})",
            "CREATE (google:Organization {name: 'Google', type: 'Company', industry: 'Technology'})",
            
            "CREATE (reading:Interest {name: 'Reading', category: 'Hobby'})",
            "CREATE (fintech:Interest {name: 'Fintech', category: 'Professional'})",
            "CREATE (climbing:Interest {name: 'Rock Climbing', category: 'Sport'})",
            "CREATE (books:Interest {name: 'Books', category: 'Hobby'})",
            
            "CREATE (python:Skill {name: 'Python', level: 'Expert'})",
            "CREATE (pm:Skill {name: 'Product Management', level: 'Senior'})",
        ]
        
        relationship_queries = [
            "MATCH (cu:Person {name: 'CurrentUser'}), (a:Person {name: 'Alice'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.9}]->(a)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (b:Person {name: 'Bob'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.8}]->(b)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (w:Person {name: 'Will'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.7}]->(w)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (c:Person {name: 'Carol'}) CREATE (cu)-[:KNOWS {context: 'mutual friends'}]->(c)",
            "MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'}) CREATE (a)-[:FRIENDS_WITH {strength: 0.6}]->(b)",
            
            "MATCH (w:Person {name: 'Will'}), (sf:Location {city: 'San Francisco'}) CREATE (w)-[:LIVES_IN]->(sf)",
            "MATCH (a:Person {name: 'Alice'}), (sf:Location {city: 'San Francisco'}) CREATE (a)-[:LIVES_IN]->(sf)",
            "MATCH (c:Person {name: 'Carol'}), (ny:Location {city: 'New York'}) CREATE (c)-[:LIVES_IN]->(ny)",
            
            "MATCH (b:Person {name: 'Bob'}), (s:Organization {name: 'Stripe'}) CREATE (b)-[:WORKS_AT {role: 'Product Manager', since: '2023'}]->(s)",
            "MATCH (a:Person {name: 'Alice'}), (g:Organization {name: 'Google'}) CREATE (a)-[:WORKS_AT {role: 'Software Engineer', since: '2022'}]->(g)",
            
            "MATCH (c:Person {name: 'Carol'}), (cornell:Organization {name: 'Cornell'}) CREATE (c)-[:WENT_TO_SCHOOL_AT {degree: 'Computer Science', year: 3}]->(cornell)",
            
            "MATCH (a:Person {name: 'Alice'}), (r:Interest {name: 'Reading'}) CREATE (a)-[:INTERESTED_IN {confidence: 0.9}]->(r)",
            "MATCH (a:Person {name: 'Alice'}), (b:Interest {name: 'Books'}) CREATE (a)-[:INTERESTED_IN {confidence: 0.9}]->(b)",
            "MATCH (b:Person {name: 'Bob'}), (f:Interest {name: 'Fintech'}) CREATE (b)-[:INTERESTED_IN {confidence: 0.95}]->(f)",
            "MATCH (w:Person {name: 'Will'}), (c:Interest {name: 'Rock Climbing'}) CREATE (w)-[:INTERESTED_IN {confidence: 0.8}]->(c)",
            
            "MATCH (a:Person {name: 'Alice'}), (p:Skill {name: 'Python'}) CREATE (a)-[:SKILLED_AT {proficiency: 'Expert'}]->(p)",
            "MATCH (b:Person {name: 'Bob'}), (pm:Skill {name: 'Product Management'}) CREATE (b)-[:SKILLED_AT {proficiency: 'Senior'}]->(pm)",
        ]
        
        check_query = "MATCH (p:Person {name: 'Alice'}) RETURN count(p) as count"
        result = await self.execute_query(check_query)
        if result and result[0]["count"] > 0:
            print("Sample data already exists, skipping creation")
            return
        
        print("Creating sample data...")
        
        for query in sample_data_queries + relationship_queries:
            try:
                await self.execute_query(query)
            except Exception as e:
                print(f"Error executing query: {query}")
                print(f"Error: {e}")
        
        print("Sample data created successfully")
