# Network Query API - FastAPI + Neo4j Backend

A hackathon-ready MVP for querying social network data using natural language, built with FastAPI, Neo4j, and OpenAI API.

## 🚀 Features

- **Natural Language Querying**: Ask questions about your network in plain English
- **Graph Database**: Neo4j stores relationships between people, organizations, interests, and locations
- **Smart Query Translation**: OpenAI API converts natural language to Cypher queries with intelligent fallbacks
- **RESTful API**: Clean FastAPI endpoints for querying and data management
- **Sample Data**: Pre-loaded with realistic social network data for testing

## 📋 User Stories Implemented

✅ **Book Club Finder**: "Who would want to join a book club?" → Returns people interested in reading/books  
✅ **Location-based Search**: "Find friends who live in San Francisco" → Returns friends in SF  
✅ **School Network**: "Find Cornell friends in their 3rd year" → Returns Cornell students  
✅ **Interest Discovery**: "What are Will's interests?" → Returns person's interests  
✅ **Professional Network**: "Who in my network has fintech experience?" → Returns people with fintech background

## 🛠 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: Neo4j Graph Database
- **AI**: OpenAI API for natural language processing
- **Dependencies**: neo4j, openai, python-dotenv, pydantic

## 🏗 Architecture

```
User Query → FastAPI → Query Processor → Neo4j Database
                    ↓
            OpenAI API (with fallbacks)
```

### Graph Schema

**Nodes**: Person, Organization, Location, Interest, Skill, Language, Club  
**Relationships**: FRIENDS_WITH, LIVES_IN, WORKS_AT, INTERESTED_IN, SKILLED_AT, etc.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Poetry
- Neo4j Database (local or cloud)
- OpenAI API Key (optional - has fallbacks)

### Installation

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j and OpenAI credentials
   ```

3. **Start Neo4j** (if using Docker):
   ```bash
   docker run --name neo4j-hackathon -p 7474:7474 -p 7687:7687 -d \
     -e NEO4J_AUTH=neo4j/password neo4j:latest
   ```

4. **Run the API**:
   ```bash
   poetry run fastapi dev app/main.py
   ```

The API will be available at `http://localhost:8000` with docs at `http://localhost:8000/docs`

## 📡 API Endpoints

### Core Endpoints

- `POST /query` - Natural language queries
- `GET /graph/stats` - Database statistics
- `POST /person` - Add new person
- `POST /relationship` - Add relationship
- `GET /healthz` - Health check

### Example Usage

```bash
# Natural language query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find friends who live in San Francisco", "user_name": "CurrentUser"}'

# Add a person
curl -X POST "http://localhost:8000/person" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "age": 25, "bio": "Software engineer"}'

# Get database stats
curl -X GET "http://localhost:8000/graph/stats"
```

## 🧪 Testing

The API includes comprehensive sample data and has been tested with all user stories:

```bash
# Test book club query
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "Who would want to join a book club?"}'

# Test location query  
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "Find friends who live in San Francisco"}'

# Test professional network
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "Who in my network has fintech experience?"}'
```

## 🌐 Deployment

### Option 1: Fly.io (Recommended)

1. Install Fly CLI
2. Run: `fly deploy`

### Option 2: Railway

1. Connect GitHub repo
2. Set environment variables
3. Deploy automatically

### Option 3: Heroku

1. Create Heroku app
2. Add Neo4j addon
3. Deploy via Git

## 🔧 Configuration

### Environment Variables

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key_here
```

### Production Notes

- Use Neo4j Aura for cloud database
- Set proper CORS origins for production
- Use environment-specific configurations
- Enable logging and monitoring

## 🎯 Hackathon Demo Script

1. **Show API docs**: Visit `/docs` endpoint
2. **Test health**: `GET /healthz`
3. **Show sample data**: `GET /graph/stats`
4. **Demo queries**:
   - "Find friends who live in San Francisco"
   - "Who would want to join a book club?"
   - "Who in my network has fintech experience?"
5. **Add new person**: `POST /person`
6. **Show generated Cypher**: Check response `cypher_used` field

## 🔮 Future Enhancements

- Discord/LinkedIn integrations
- Real-time relationship strength scoring
- Advanced entity resolution
- Multi-tenant support
- Graph visualization frontend
- Mobile app integration

## 📄 License

MIT License - Perfect for hackathon use!
