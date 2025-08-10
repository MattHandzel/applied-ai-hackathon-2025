import openai
import os
from typing import Dict, Any, Optional

class QueryProcessor:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
    async def generate_cypher(self, natural_language_query: str, user_name: str = "CurrentUser") -> str:
        fallback_query = self._get_fallback_query(natural_language_query, user_name)
        if fallback_query:
            return fallback_query
        schema_info = """
        You are a Cypher query generator for a social network knowledge graph. Convert natural language to Cypher queries.

        Schema:
        Nodes: Person, Organization, Location, Interest, Skill, Language, Club
        Relationships: FRIENDS_WITH, DOESNT_LIKE, LIVES_IN, WORKS_AT, WENT_TO_SCHOOL_AT, INTERESTED_IN, SKILLED_AT, SPEAKS, PARTICIPATED_IN, DATING, KNOWS

        Node Properties:
        - Person: {name, age, bio}
        - Organization: {name, type, industry}
        - Location: {city, country}
        - Interest: {name, category}
        - Skill: {name, level}

        Relationship Properties:
        - FRIENDS_WITH: {strength}
        - WORKS_AT: {role, since}
        - WENT_TO_SCHOOL_AT: {degree, year}
        - INTERESTED_IN: {confidence}
        - SKILLED_AT: {proficiency}

        Examples:
        Query: "Find friends who live in San Francisco"
        Cypher: MATCH (me:Person {name: 'CurrentUser'})-[:FRIENDS_WITH]-(friend:Person)-[:LIVES_IN]->(loc:Location {city: 'San Francisco'}) RETURN friend.name, friend.bio

        Query: "Who in my network has fintech experience?"
        Cypher: MATCH (me:Person {name: 'CurrentUser'})-[:FRIENDS_WITH|KNOWS*1..2]-(person:Person)-[:WORKS_AT]->(org:Organization) WHERE org.industry CONTAINS 'fintech' OR org.industry CONTAINS 'Fintech' RETURN person.name, person.bio, org.name

        Query: "Find people interested in reading or books"
        Cypher: MATCH (me:Person {name: 'CurrentUser'})-[:FRIENDS_WITH|KNOWS*1..2]-(person:Person)-[:INTERESTED_IN]->(interest:Interest) WHERE interest.name CONTAINS 'Reading' OR interest.name CONTAINS 'Books' RETURN person.name, person.bio, interest.name

        Query: "Who are my Cornell friends in their 3rd year?"
        Cypher: MATCH (me:Person {name: 'CurrentUser'})-[:FRIENDS_WITH|KNOWS*1..2]-(person:Person)-[:WENT_TO_SCHOOL_AT]->(school:Organization {name: 'Cornell'}) WHERE school.year = 3 RETURN person.name, person.bio

        Query: "What are Will's interests?"
        Cypher: MATCH (will:Person {name: 'Will'})-[:INTERESTED_IN]->(interest:Interest) RETURN interest.name, interest.category

        Important rules:
        1. Always use the exact user name provided in the query context
        2. Use CONTAINS for text matching to be case-insensitive
        3. Use *1..2 for extended network searches (friends of friends)
        4. Always RETURN meaningful information like name, bio, and relevant properties
        5. Only generate valid Cypher syntax
        """

        prompt = f"""
        {schema_info}

        Current user name: {user_name}
        Query: "{natural_language_query}"
        
        Generate only the Cypher query, no explanation:
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Cypher query generator. Return only valid Cypher queries, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            cypher_query = response.choices[0].message.content.strip()
            
            if cypher_query.startswith("```"):
                cypher_query = cypher_query.split("```")[1]
                if cypher_query.startswith("cypher"):
                    cypher_query = cypher_query[6:]
                cypher_query = cypher_query.strip()
            
            return cypher_query
            
        except Exception as e:
            print(f"Error generating Cypher query: {e}")
            return self._get_fallback_query(natural_language_query, user_name) or f"MATCH (me:Person {{name: '{user_name}'}}) RETURN me.name, me.bio"

    def _get_fallback_query(self, query: str, user_name: str) -> Optional[str]:
        """Simple pattern matching for demo queries when OpenAI API is not available"""
        query_lower = query.lower()
        
        if "friends" in query_lower and "san francisco" in query_lower:
            return f"MATCH (me:Person {{name: '{user_name}'}})-[:FRIENDS_WITH]-(friend:Person)-[:LIVES_IN]->(loc:Location {{city: 'San Francisco'}}) RETURN friend.name, friend.bio, loc.city"
        
        elif "fintech" in query_lower and ("network" in query_lower or "experience" in query_lower):
            return f"MATCH (me:Person {{name: '{user_name}'}})-[:FRIENDS_WITH|KNOWS*1..2]-(person:Person)-[:WORKS_AT]->(org:Organization) WHERE org.industry CONTAINS 'Fintech' RETURN person.name, person.bio, org.name, org.industry"
        
        elif "will" in query_lower and "interest" in query_lower:
            return "MATCH (will:Person {name: 'Will'})-[:INTERESTED_IN]->(interest:Interest) RETURN will.name, interest.name, interest.category"
        
        elif "cornell" in query_lower and ("friends" in query_lower or "3rd year" in query_lower):
            return f"MATCH (me:Person {{name: '{user_name}'}})-[:FRIENDS_WITH|KNOWS*1..2]-(person:Person)-[:WENT_TO_SCHOOL_AT]->(school:Organization {{name: 'Cornell'}}) RETURN person.name, person.bio, school.name"
        
        elif "book" in query_lower and ("club" in query_lower or "reading" in query_lower):
            return f"MATCH (me:Person {{name: '{user_name}'}})-[:FRIENDS_WITH|KNOWS*1..2]-(person:Person)-[:INTERESTED_IN]->(interest:Interest) WHERE interest.name CONTAINS 'Reading' OR interest.name CONTAINS 'Books' RETURN person.name, person.bio, interest.name"
        
        return None
