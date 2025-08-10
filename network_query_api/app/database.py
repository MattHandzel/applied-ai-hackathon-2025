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
            
            "CREATE (david:Person {name: 'David', age: 29, bio: 'Venture capitalist, Stanford MBA'})",
            "CREATE (emma:Person {name: 'Emma', age: 26, bio: 'UX designer, loves photography and travel'})",
            "CREATE (frank:Person {name: 'Frank', age: 31, bio: 'Startup founder, previously at Meta'})",
            "CREATE (grace:Person {name: 'Grace', age: 23, bio: 'Cornell student, 2nd year Economics'})",
            "CREATE (henry:Person {name: 'Henry', age: 30, bio: 'Data scientist at Coinbase, crypto enthusiast'})",
            "CREATE (iris:Person {name: 'Iris', age: 27, bio: 'Marketing manager, book club organizer'})",
            "CREATE (jack:Person {name: 'Jack', age: 25, bio: 'Software engineer at Airbnb, rock climbing buddy'})",
            "CREATE (kate:Person {name: 'Kate', age: 28, bio: 'Product designer, lives in NYC, Cornell alum'})",
            "CREATE (leo:Person {name: 'Leo', age: 32, bio: 'Investment banker, fintech advisor'})",
            "CREATE (maya:Person {name: 'Maya', age: 24, bio: 'Graduate student at Stanford, AI researcher'})",
            
            "CREATE (sf:Location {city: 'San Francisco', country: 'USA'})",
            "CREATE (ny:Location {city: 'New York', country: 'USA'})",
            "CREATE (la:Location {city: 'Los Angeles', country: 'USA'})",
            "CREATE (seattle:Location {city: 'Seattle', country: 'USA'})",
            "CREATE (austin:Location {city: 'Austin', country: 'USA'})",
            "CREATE (boston:Location {city: 'Boston', country: 'USA'})",
            
            "CREATE (stripe:Organization {name: 'Stripe', type: 'Company', industry: 'Fintech'})",
            "CREATE (cornell:Organization {name: 'Cornell', type: 'University', industry: 'Education'})",
            "CREATE (google:Organization {name: 'Google', type: 'Company', industry: 'Technology'})",
            "CREATE (stanford:Organization {name: 'Stanford', type: 'University', industry: 'Education'})",
            "CREATE (meta:Organization {name: 'Meta', type: 'Company', industry: 'Technology'})",
            "CREATE (airbnb:Organization {name: 'Airbnb', type: 'Company', industry: 'Technology'})",
            "CREATE (coinbase:Organization {name: 'Coinbase', type: 'Company', industry: 'Fintech'})",
            "CREATE (a16z:Organization {name: 'Andreessen Horowitz', type: 'VC Firm', industry: 'Venture Capital'})",
            "CREATE (sequoia:Organization {name: 'Sequoia Capital', type: 'VC Firm', industry: 'Venture Capital'})",
            
            "CREATE (reading:Interest {name: 'Reading', category: 'Hobby'})",
            "CREATE (fintech:Interest {name: 'Fintech', category: 'Professional'})",
            "CREATE (climbing:Interest {name: 'Rock Climbing', category: 'Sport'})",
            "CREATE (books:Interest {name: 'Books', category: 'Hobby'})",
            "CREATE (photography:Interest {name: 'Photography', category: 'Hobby'})",
            "CREATE (travel:Interest {name: 'Travel', category: 'Hobby'})",
            "CREATE (crypto:Interest {name: 'Cryptocurrency', category: 'Professional'})",
            "CREATE (ai:Interest {name: 'Artificial Intelligence', category: 'Professional'})",
            "CREATE (startups:Interest {name: 'Startups', category: 'Professional'})",
            "CREATE (investing:Interest {name: 'Investing', category: 'Professional'})",
            "CREATE (design:Interest {name: 'Design', category: 'Professional'})",
            "CREATE (marketing:Interest {name: 'Marketing', category: 'Professional'})",
            
            "CREATE (python:Skill {name: 'Python', level: 'Expert'})",
            "CREATE (pm:Skill {name: 'Product Management', level: 'Senior'})",
            "CREATE (javascript:Skill {name: 'JavaScript', level: 'Expert'})",
            "CREATE (react:Skill {name: 'React', level: 'Advanced'})",
            "CREATE (design_skill:Skill {name: 'UI/UX Design', level: 'Expert'})",
            "CREATE (ml:Skill {name: 'Machine Learning', level: 'Advanced'})",
            "CREATE (finance:Skill {name: 'Finance', level: 'Expert'})",
            "CREATE (marketing_skill:Skill {name: 'Digital Marketing', level: 'Senior'})",
        ]
        
        relationship_queries = [
            "MATCH (cu:Person {name: 'CurrentUser'}), (a:Person {name: 'Alice'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.9}]->(a)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (b:Person {name: 'Bob'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.8}]->(b)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (w:Person {name: 'Will'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.7}]->(w)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (d:Person {name: 'David'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.8}]->(d)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (e:Person {name: 'Emma'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.7}]->(e)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (i:Person {name: 'Iris'}) CREATE (cu)-[:FRIENDS_WITH {strength: 0.6}]->(i)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (c:Person {name: 'Carol'}) CREATE (cu)-[:KNOWS {context: 'mutual friends'}]->(c)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (f:Person {name: 'Frank'}) CREATE (cu)-[:KNOWS {context: 'startup community'}]->(f)",
            "MATCH (cu:Person {name: 'CurrentUser'}), (k:Person {name: 'Kate'}) CREATE (cu)-[:KNOWS {context: 'Cornell alumni'}]->(k)",
            
            "MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'}) CREATE (a)-[:FRIENDS_WITH {strength: 0.6}]->(b)",
            "MATCH (w:Person {name: 'Will'}), (j:Person {name: 'Jack'}) CREATE (w)-[:FRIENDS_WITH {strength: 0.9}]->(j)",
            "MATCH (c:Person {name: 'Carol'}), (g:Person {name: 'Grace'}) CREATE (c)-[:FRIENDS_WITH {strength: 0.8}]->(g)",
            "MATCH (d:Person {name: 'David'}), (l:Person {name: 'Leo'}) CREATE (d)-[:FRIENDS_WITH {strength: 0.7}]->(l)",
            "MATCH (e:Person {name: 'Emma'}), (i:Person {name: 'Iris'}) CREATE (e)-[:FRIENDS_WITH {strength: 0.8}]->(i)",
            "MATCH (f:Person {name: 'Frank'}), (h:Person {name: 'Henry'}) CREATE (f)-[:FRIENDS_WITH {strength: 0.6}]->(h)",
            "MATCH (a:Person {name: 'Alice'}), (i:Person {name: 'Iris'}) CREATE (a)-[:FRIENDS_WITH {strength: 0.7}]->(i)",
            "MATCH (b:Person {name: 'Bob'}), (h:Person {name: 'Henry'}) CREATE (b)-[:FRIENDS_WITH {strength: 0.5}]->(h)",
            
            "MATCH (w:Person {name: 'Will'}), (sf:Location {city: 'San Francisco'}) CREATE (w)-[:LIVES_IN]->(sf)",
            "MATCH (a:Person {name: 'Alice'}), (sf:Location {city: 'San Francisco'}) CREATE (a)-[:LIVES_IN]->(sf)",
            "MATCH (j:Person {name: 'Jack'}), (sf:Location {city: 'San Francisco'}) CREATE (j)-[:LIVES_IN]->(sf)",
            "MATCH (c:Person {name: 'Carol'}), (ny:Location {city: 'New York'}) CREATE (c)-[:LIVES_IN]->(ny)",
            "MATCH (k:Person {name: 'Kate'}), (ny:Location {city: 'New York'}) CREATE (k)-[:LIVES_IN]->(ny)",
            "MATCH (l:Person {name: 'Leo'}), (ny:Location {city: 'New York'}) CREATE (l)-[:LIVES_IN]->(ny)",
            "MATCH (e:Person {name: 'Emma'}), (la:Location {city: 'Los Angeles'}) CREATE (e)-[:LIVES_IN]->(la)",
            "MATCH (d:Person {name: 'David'}), (seattle:Location {city: 'Seattle'}) CREATE (d)-[:LIVES_IN]->(seattle)",
            "MATCH (f:Person {name: 'Frank'}), (austin:Location {city: 'Austin'}) CREATE (f)-[:LIVES_IN]->(austin)",
            "MATCH (h:Person {name: 'Henry'}), (sf:Location {city: 'San Francisco'}) CREATE (h)-[:LIVES_IN]->(sf)",
            "MATCH (m:Person {name: 'Maya'}), (boston:Location {city: 'Boston'}) CREATE (m)-[:LIVES_IN]->(boston)",
            
            "MATCH (b:Person {name: 'Bob'}), (s:Organization {name: 'Stripe'}) CREATE (b)-[:WORKS_AT {role: 'Product Manager', since: '2023'}]->(s)",
            "MATCH (a:Person {name: 'Alice'}), (g:Organization {name: 'Google'}) CREATE (a)-[:WORKS_AT {role: 'Software Engineer', since: '2022'}]->(g)",
            "MATCH (j:Person {name: 'Jack'}), (airbnb:Organization {name: 'Airbnb'}) CREATE (j)-[:WORKS_AT {role: 'Software Engineer', since: '2024'}]->(airbnb)",
            "MATCH (h:Person {name: 'Henry'}), (coinbase:Organization {name: 'Coinbase'}) CREATE (h)-[:WORKS_AT {role: 'Data Scientist', since: '2023'}]->(coinbase)",
            "MATCH (d:Person {name: 'David'}), (a16z:Organization {name: 'Andreessen Horowitz'}) CREATE (d)-[:WORKS_AT {role: 'Partner', since: '2022'}]->(a16z)",
            "MATCH (l:Person {name: 'Leo'}), (sequoia:Organization {name: 'Sequoia Capital'}) CREATE (l)-[:WORKS_AT {role: 'Principal', since: '2021'}]->(sequoia)",
            "MATCH (f:Person {name: 'Frank'}), (meta:Organization {name: 'Meta'}) CREATE (f)-[:WORKED_AT {role: 'Senior Engineer', from: '2020', to: '2023'}]->(meta)",
            
            "MATCH (c:Person {name: 'Carol'}), (cornell:Organization {name: 'Cornell'}) CREATE (c)-[:WENT_TO_SCHOOL_AT {degree: 'Computer Science', year: 3}]->(cornell)",
            "MATCH (g:Person {name: 'Grace'}), (cornell:Organization {name: 'Cornell'}) CREATE (g)-[:WENT_TO_SCHOOL_AT {degree: 'Economics', year: 2}]->(cornell)",
            "MATCH (k:Person {name: 'Kate'}), (cornell:Organization {name: 'Cornell'}) CREATE (k)-[:WENT_TO_SCHOOL_AT {degree: 'Design', graduated: '2020'}]->(cornell)",
            "MATCH (d:Person {name: 'David'}), (stanford:Organization {name: 'Stanford'}) CREATE (d)-[:WENT_TO_SCHOOL_AT {degree: 'MBA', graduated: '2021'}]->(stanford)",
            "MATCH (m:Person {name: 'Maya'}), (stanford:Organization {name: 'Stanford'}) CREATE (m)-[:WENT_TO_SCHOOL_AT {degree: 'PhD AI', year: 2}]->(stanford)",
            
            "MATCH (a:Person {name: 'Alice'}), (r:Interest {name: 'Reading'}) CREATE (a)-[:INTERESTED_IN {confidence: 0.9}]->(r)",
            "MATCH (a:Person {name: 'Alice'}), (b:Interest {name: 'Books'}) CREATE (a)-[:INTERESTED_IN {confidence: 0.9}]->(b)",
            "MATCH (i:Person {name: 'Iris'}), (b:Interest {name: 'Books'}) CREATE (i)-[:INTERESTED_IN {confidence: 0.95}]->(b)",
            "MATCH (i:Person {name: 'Iris'}), (r:Interest {name: 'Reading'}) CREATE (i)-[:INTERESTED_IN {confidence: 0.95}]->(r)",
            "MATCH (b:Person {name: 'Bob'}), (f:Interest {name: 'Fintech'}) CREATE (b)-[:INTERESTED_IN {confidence: 0.95}]->(f)",
            "MATCH (h:Person {name: 'Henry'}), (f:Interest {name: 'Fintech'}) CREATE (h)-[:INTERESTED_IN {confidence: 0.9}]->(f)",
            "MATCH (h:Person {name: 'Henry'}), (crypto:Interest {name: 'Cryptocurrency'}) CREATE (h)-[:INTERESTED_IN {confidence: 0.95}]->(crypto)",
            "MATCH (l:Person {name: 'Leo'}), (f:Interest {name: 'Fintech'}) CREATE (l)-[:INTERESTED_IN {confidence: 0.8}]->(f)",
            "MATCH (l:Person {name: 'Leo'}), (inv:Interest {name: 'Investing'}) CREATE (l)-[:INTERESTED_IN {confidence: 0.9}]->(inv)",
            "MATCH (d:Person {name: 'David'}), (inv:Interest {name: 'Investing'}) CREATE (d)-[:INTERESTED_IN {confidence: 0.95}]->(inv)",
            "MATCH (d:Person {name: 'David'}), (startups:Interest {name: 'Startups'}) CREATE (d)-[:INTERESTED_IN {confidence: 0.9}]->(startups)",
            "MATCH (f:Person {name: 'Frank'}), (startups:Interest {name: 'Startups'}) CREATE (f)-[:INTERESTED_IN {confidence: 0.95}]->(startups)",
            "MATCH (w:Person {name: 'Will'}), (c:Interest {name: 'Rock Climbing'}) CREATE (w)-[:INTERESTED_IN {confidence: 0.8}]->(c)",
            "MATCH (j:Person {name: 'Jack'}), (c:Interest {name: 'Rock Climbing'}) CREATE (j)-[:INTERESTED_IN {confidence: 0.9}]->(c)",
            "MATCH (e:Person {name: 'Emma'}), (photo:Interest {name: 'Photography'}) CREATE (e)-[:INTERESTED_IN {confidence: 0.9}]->(photo)",
            "MATCH (e:Person {name: 'Emma'}), (travel:Interest {name: 'Travel'}) CREATE (e)-[:INTERESTED_IN {confidence: 0.8}]->(travel)",
            "MATCH (k:Person {name: 'Kate'}), (design:Interest {name: 'Design'}) CREATE (k)-[:INTERESTED_IN {confidence: 0.95}]->(design)",
            "MATCH (m:Person {name: 'Maya'}), (ai:Interest {name: 'Artificial Intelligence'}) CREATE (m)-[:INTERESTED_IN {confidence: 0.95}]->(ai)",
            
            "MATCH (a:Person {name: 'Alice'}), (p:Skill {name: 'Python'}) CREATE (a)-[:SKILLED_AT {proficiency: 'Expert'}]->(p)",
            "MATCH (j:Person {name: 'Jack'}), (p:Skill {name: 'Python'}) CREATE (j)-[:SKILLED_AT {proficiency: 'Advanced'}]->(p)",
            "MATCH (j:Person {name: 'Jack'}), (js:Skill {name: 'JavaScript'}) CREATE (j)-[:SKILLED_AT {proficiency: 'Expert'}]->(js)",
            "MATCH (a:Person {name: 'Alice'}), (js:Skill {name: 'JavaScript'}) CREATE (a)-[:SKILLED_AT {proficiency: 'Advanced'}]->(js)",
            "MATCH (b:Person {name: 'Bob'}), (pm:Skill {name: 'Product Management'}) CREATE (b)-[:SKILLED_AT {proficiency: 'Senior'}]->(pm)",
            "MATCH (e:Person {name: 'Emma'}), (design_skill:Skill {name: 'UI/UX Design'}) CREATE (e)-[:SKILLED_AT {proficiency: 'Expert'}]->(design_skill)",
            "MATCH (k:Person {name: 'Kate'}), (design_skill:Skill {name: 'UI/UX Design'}) CREATE (k)-[:SKILLED_AT {proficiency: 'Expert'}]->(design_skill)",
            "MATCH (h:Person {name: 'Henry'}), (ml:Skill {name: 'Machine Learning'}) CREATE (h)-[:SKILLED_AT {proficiency: 'Advanced'}]->(ml)",
            "MATCH (m:Person {name: 'Maya'}), (ml:Skill {name: 'Machine Learning'}) CREATE (m)-[:SKILLED_AT {proficiency: 'Expert'}]->(ml)",
            "MATCH (d:Person {name: 'David'}), (finance:Skill {name: 'Finance'}) CREATE (d)-[:SKILLED_AT {proficiency: 'Expert'}]->(finance)",
            "MATCH (l:Person {name: 'Leo'}), (finance:Skill {name: 'Finance'}) CREATE (l)-[:SKILLED_AT {proficiency: 'Expert'}]->(finance)",
            "MATCH (i:Person {name: 'Iris'}), (marketing_skill:Skill {name: 'Digital Marketing'}) CREATE (i)-[:SKILLED_AT {proficiency: 'Senior'}]->(marketing_skill)",
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
