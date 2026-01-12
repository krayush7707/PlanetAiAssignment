# GenAI Stack - Architecture & Design Document
## High Level Design (HLD) & Low Level Design (LLD)

**Project**: No-Code/Low-Code Workflow Builder for Intelligent AI Workflows  
**Author**: Ayush Kumar (krayush7707)  
**Date**: January 2026  
**Repository**: https://github.com/krayush7707/PlanetAiAssignment

---

## Table of Contents
1. [High Level Design (HLD)](#high-level-design)
2. [Low Level Design (LLD)](#low-level-design)
3. [Database Design](#database-design)
4. [API Design](#api-design)
5. [Deployment Architecture](#deployment-architecture)

---

# High Level Design (HLD)

## 1. System Overview

GenAI Stack is a full-stack web application that enables users to visually create intelligent workflows by connecting pre-built components. The system supports document processing, vector search, LLM integration, and web search capabilities.

### Key Features
- Visual drag-and-drop workflow builder
- PDF document processing with RAG (Retrieval Augmented Generation)
- OpenAI GPT integration for intelligent responses
- Web search integration via SerpAPI
- Persistent chat history
- Workflow validation and execution engine

---

## 2. System Architecture

### 2.1 Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION TIER                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │         React Frontend (Port 80)                    │    │
│  │  - React Flow Canvas (Workflow Builder)            │    │
│  │  - Component Library (Drag & Drop)                 │    │
│  │  - Chat Interface                                   │    │
│  │  - State Management (Zustand)                      │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION TIER                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │         FastAPI Backend (Port 8000)                 │    │
│  │  ┌──────────────────────────────────────────┐      │    │
│  │  │   API Layer (REST Endpoints)             │      │    │
│  │  ├──────────────────────────────────────────┤      │    │
│  │  │   Business Logic Layer                   │      │    │
│  │  │   - Workflow Validator                   │      │    │
│  │  │   - Workflow Executor                    │      │    │
│  │  │   - Component Factory                    │      │    │
│  │  ├──────────────────────────────────────────┤      │    │
│  │  │   Component Layer                        │      │    │
│  │  │   - User Query Component                 │      │    │
│  │  │   - Knowledge Base Component             │      │    │
│  │  │   - LLM Engine Component                 │      │    │
│  │  │   - Output Component                     │      │    │
│  │  └──────────────────────────────────────────┘      │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA TIER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │   ChromaDB   │  │  File System │      │
│  │   (Port      │  │   (Vector    │  │  (Uploads)   │      │
│  │    5432)     │  │    Store)    │  │              │      │
│  │              │  │              │  │              │      │
│  │ - Workflows  │  │ - Embeddings │  │ - PDF Files  │      │
│  │ - Documents  │  │ - Documents  │  │              │      │
│  │ - Chat Logs  │  │ - Metadata   │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 External Integrations

```
┌──────────────────────────────────────────┐
│      External APIs                        │
│  ┌────────────┐  ┌──────────┐           │
│  │  OpenAI    │  │ SerpAPI  │           │
│  │   API      │  │   API    │           │
│  │            │  │          │           │
│  │ - GPT-4o   │  │ - Google │           │
│  │ - Embeddings│  │  Search  │           │
│  └────────────┘  └──────────┘           │
└──────────────────────────────────────────┘
         ↑                    ↑
         └────────┬───────────┘
                  │
         FastAPI Backend
```

---

## 3. Component Architecture

### 3.1 Workflow Components

```
┌─────────────────────────────────────────────────────┐
│              Base Component (Abstract)               │
│  - execute(input_data) → output_data                │
│  - validate_config() → boolean                      │
│  - get_output_schema() → schema                     │
└─────────────────────────────────────────────────────┘
                         ↑
        ┌────────────────┼────────────────┬───────────┐
        │                │                │           │
┌───────┴────────┐ ┌────┴──────┐ ┌──────┴─────┐ ┌───┴────┐
│  User Query    │ │ Knowledge │ │ LLM Engine │ │ Output │
│  Component     │ │   Base    │ │ Component  │ │ Comp.  │
│                │ │ Component │ │            │ │        │
│ - Accept query │ │ - Upload  │ │ - Call GPT │ │ - Format│
│ - Pass forward │ │ - Extract │ │ - Web      │ │ - Return│
│                │ │ - Embed   │ │   Search   │ │ result │
│                │ │ - Retrieve│ │ - Merge    │ │        │
└────────────────┘ └───────────┘ └────────────┘ └────────┘
```

### 3.2 Data Flow

```
User Query Input
      ↓
┌─────────────┐
│ User Query  │
│ Component   │
└──────┬──────┘
       │ {query: "..."}
       ↓
┌─────────────┐
│ Knowledge   │
│ Base        │────→ ChromaDB (Vector Search)
│ Component   │←──── Relevant Chunks
└──────┬──────┘
       │ {query: "...", context: "..."}
       ↓
┌─────────────┐
│ LLM Engine  │────→ OpenAI API / SerpAPI
│ Component   │←──── Generated Response
└──────┬──────┘
       │ {response: "..."}
       ↓
┌─────────────┐
│ Output      │
│ Component   │
└──────┬──────┘
       │
       ↓
  Final Response to User
```

---

## 4. Technology Stack

### Frontend
- **Framework**: React 19 with Vite
- **UI Library**: React Flow for workflow visualization
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Data Fetching**: TanStack React Query
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Vector Store**: ChromaDB
- **Document Processing**: PyMuPDF
- **LLM Integration**: OpenAI Python SDK
- **Web Search**: SerpAPI (google-search-results)
- **Validation**: Pydantic

### DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (for frontend)
- **API Server**: Uvicorn (ASGI)

---

## 5. Deployment Architecture

```
┌───────────────────────────────────────────────────┐
│                Docker Host                         │
│                                                    │
│  ┌──────────────┐      ┌──────────────┐          │
│  │   Nginx      │      │   FastAPI    │          │
│  │  Container   │─────▶│  Container   │          │
│  │  (Port 80)   │      │  (Port 8000) │          │
│  └──────────────┘      └───────┬──────┘          │
│                                 │                  │
│  ┌──────────────┐      ┌───────┴──────┐          │
│  │  PostgreSQL  │◀─────│              │          │
│  │  Container   │      │              │          │
│  │  (Port 5432) │      │              │          │
│  └──────────────┘      │              │          │
│                        │              │          │
│  ┌──────────────┐      │              │          │
│  │   ChromaDB   │◀─────┘              │          │
│  │   (Embedded) │                     │          │
│  └──────────────┘                     │          │
│                                       │          │
│  Volumes:                             │          │
│  - postgres_data                      │          │
│  - backend_uploads                    │          │
│  - chroma_data                        │          │
└───────────────────────────────────────────────────┘
```

---

# Low Level Design (LLD)

## 1. Module Details

### 1.1 Backend Module Structure

```
backend/
├── main.py                    # FastAPI application entry
├── config.py                  # Configuration management
│
├── app/
│   ├── api/                   # API endpoints
│   │   ├── documents.py       # Document management
│   │   ├── workflows.py       # Workflow CRUD
│   │   ├── chat.py           # Chat execution
│   │   └── health.py         # Health checks
│   │
│   ├── components/           # Workflow components
│   │   ├── base.py          # Abstract base class
│   │   ├── user_query.py    # User input handler
│   │   ├── knowledgebase.py # RAG implementation
│   │   ├── llm_engine.py    # LLM integration
│   │   └── output.py        # Output formatter
│   │
│   ├── workflow/            # Workflow engine
│   │   ├── validator.py     # Graph validation
│   │   └── executor.py      # Execution orchestration
│   │
│   ├── database/            # Data layer
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── connection.py    # DB connection
│   │   └── schemas.py       # Pydantic schemas
│   │
│   └── vector_store/        # Vector operations
│       └── chromadb_client.py
```

### 1.2 Frontend Module Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main application
│   ├── index.css            # Global styles
│   │
│   ├── services/            # API layer
│   │   └── api.js          # Axios client
│   │
│   ├── store/              # State management
│   │   └── workflowStore.js # Zustand store
│   │
│   ├── pages/              # Page components
│   │   ├── MyStacksPage   # Workflow list
│   │   └── WorkflowBuilder # Visual editor
│   │
│   └── components/         # Reusable components
│       ├── ChatModal      # Chat interface
│       └── ComponentLibrary # Drag sources
```

---

## 2. Class Diagrams

### 2.1 Component Class Hierarchy

```
┌─────────────────────────────────────────┐
│          BaseComponent                   │
├─────────────────────────────────────────┤
│ # node_id: str                          │
│ # config: Dict[str, Any]                │
│ # component_type: str                   │
├─────────────────────────────────────────┤
│ + __init__(node_id, config)             │
│ + execute(input_data) → Any             │
│ + validate_config() → bool              │
│ + get_output_schema() → Dict            │
└─────────────────────────────────────────┘
              ↑
              │ inherits
     ┌────────┼────────┬────────┐
     │        │        │        │
┌────┴───┐ ┌─┴──────┐ ┌┴──────┐ ┌┴──────┐
│ User   │ │Knowledge│ │ LLM   │ │Output │
│ Query  │ │ Base   │ │Engine │ │       │
└────────┘ └────────┘ └───────┘ └───────┘
```

### 2.2 Database Models

```
┌──────────────────────────┐
│       Document           │
├──────────────────────────┤
│ + id: UUID (PK)         │
│ + filename: str         │
│ + file_path: str        │
│ + file_size: int        │
│ + uploaded_at: datetime │
│ + processed: bool       │
│ + chunk_count: int      │
│ + collection_name: str  │
└──────────────────────────┘

┌──────────────────────────┐
│       Workflow           │
├──────────────────────────┤
│ + id: UUID (PK)         │
│ + name: str             │
│ + description: str      │
│ + nodes: JSONB          │
│ + edges: JSONB          │
│ + is_valid: bool        │
│ + created_at: datetime  │
│ + updated_at: datetime  │
└──────────┬───────────────┘
           │ 1:N
           ↓
┌──────────────────────────┐
│     ChatSession          │
├──────────────────────────┤
│ + id: UUID (PK)         │
│ + workflow_id: UUID (FK)│
│ + created_at: datetime  │
└──────────┬───────────────┘
           │ 1:N
           ↓
┌──────────────────────────┐
│     ChatMessage          │
├──────────────────────────┤
│ + id: UUID (PK)         │
│ + session_id: UUID (FK) │
│ + role: str             │
│ + content: text         │
│ + created_at: datetime  │
└──────────────────────────┘
```

---

## 3. Sequence Diagrams

### 3.1 Document Upload Flow

```
User      Frontend    Backend API   PyMuPDF   OpenAI   ChromaDB   PostgreSQL
 │           │            │            │         │         │          │
 │ Upload PDF│            │            │         │         │          │
 ├──────────>│            │            │         │         │          │
 │           │ POST /documents/upload  │         │         │          │
 │           ├───────────>│            │         │         │          │
 │           │            │ Save to FS │         │         │          │
 │           │            ├───────────>│         │         │          │
 │           │            │            │         │         │          │
 │           │            │ Extract text         │         │          │
 │           │            ├────────────┤         │         │          │
 │           │            │<───────────┤         │         │          │
 │           │            │            │         │         │          │
 │           │            │ Chunk text │         │         │          │
 │           │            ├────────────┤         │         │          │
 │           │            │            │         │         │          │
 │           │            │ Generate embeddings  │         │          │
 │           │            ├─────────────────────>│         │          │
 │           │            │<─────────────────────┤         │          │
 │           │            │                      │         │          │
 │           │            │ Store embeddings + metadata    │          │
 │           │            ├────────────────────────────────>│          │
 │           │            │                               │          │
 │           │            │ Save document metadata                   │
 │           │            ├─────────────────────────────────────────>│
 │           │            │<─────────────────────────────────────────┤
 │           │<───────────┤            │         │         │          │
 │<──────────┤            │            │         │         │          │
 │  Success  │            │            │         │         │          │
```

### 3.2 Chat Execution Flow

```
User   Frontend   Backend API   Workflow   Components   LLM/ChromaDB   PostgreSQL
 │        │            │         Executor      │              │            │
 │ Send   │            │            │          │              │            │
 │ Query  │            │            │          │              │            │
 ├───────>│            │            │          │              │            │
 │        │ POST /chat/execute     │          │              │            │
 │        ├───────────>│            │          │              │            │
 │        │            │ Get workflow          │              │            │
 │        │            ├──────────────────────────────────────────────────>│
 │        │            │<──────────────────────────────────────────────────┤
 │        │            │            │          │              │            │
 │        │            │ Validate   │          │              │            │
 │        │            ├───────────>│          │              │            │
 │        │            │<───────────┤          │              │            │
 │        │            │            │          │              │            │
 │        │            │ Execute workflow      │              │            │
 │        │            ├───────────>│          │              │            │
 │        │            │            │ UserQuery.execute()     │            │
 │        │            │            ├─────────>│              │            │
 │        │            │            │<─────────┤              │            │
 │        │            │            │          │              │            │
 │        │            │            │ KB.execute()            │            │
 │        │            │            ├─────────>│              │            │
 │        │            │            │          │ Query vectors│            │
 │        │            │            │          ├─────────────>│            │
 │        │            │            │          │<─────────────┤            │
 │        │            │            │<─────────┤              │            │
 │        │            │            │          │              │            │
 │        │            │            │ LLM.execute()           │            │
 │        │            │            ├─────────>│              │            │
 │        │            │            │          │ Call GPT API │            │
 │        │            │            │          ├─────────────>│            │
 │        │            │            │          │<─────────────┤            │
 │        │            │            │<─────────┤              │            │
 │        │            │            │          │              │            │
 │        │            │            │ Output.execute()        │            │
 │        │            │            ├─────────>│              │            │
 │        │            │            │<─────────┤              │            │
 │        │            │<───────────┤          │              │            │
 │        │            │            │          │              │            │
 │        │            │ Save chat messages    │              │            │
 │        │            ├──────────────────────────────────────────────────>│
 │        │<───────────┤            │          │              │            │
 │<───────┤            │            │          │              │            │
│ Display │            │            │          │              │            │
│ Response│            │            │          │              │            │
```

---

# Database Design

## 1. Entity-Relationship Diagram

```
┌─────────────┐
│  Document   │
│             │
│ PK: id      │
└─────────────┘


┌─────────────┐           ┌──────────────┐           ┌──────────────┐
│  Workflow   │ 1     N   │ ChatSession  │ 1     N   │ ChatMessage  │
│             │───────────│              │───────────│              │
│ PK: id      │           │ PK: id       │           │ PK: id       │
│             │           │ FK: workflow │           │ FK: session  │
└─────────────┘           └──────────────┘           └──────────────┘
```

## 2. Table Schemas

### documents
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    chunk_count INTEGER DEFAULT 0,
    collection_name VARCHAR(100)
);
```

### workflows
```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    nodes JSONB NOT NULL DEFAULT '[]',
    edges JSONB NOT NULL DEFAULT '[]',
    is_valid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### chat_sessions
```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### chat_messages
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# API Design

## 1. API Endpoints

### Document Management

#### POST /documents/upload
**Description**: Upload and process a PDF document  
**Content-Type**: multipart/form-data  
**Request Body**:
```
file: <PDF file>
```
**Response**:
```json
{
  "id": "uuid",
  "filename": "document.pdf",
  "file_size": 12345,
  "uploaded_at": "2026-01-12T10:00:00",
  "processed": true,
  "chunk_count": 25,
  "collection_name": "doc_uuid"
}
```

#### GET /documents/
**Description**: List all documents  
**Response**:
```json
{
  "documents": [...]
}
```

#### DELETE /documents/{id}
**Description**: Delete a document  
**Response**:
```json
{
  "message": "Document deleted successfully"
}
```

---

### Workflow Management

#### POST /workflows/
**Description**: Create a new workflow  
**Request Body**:
```json
{
  "name": "Chat With PDF",
  "description": "RAG-based PDF Q&A",
  "nodes": [...],
  "edges": [...]
}
```
**Response**:
```json
{
  "id": "uuid",
  "name": "Chat With PDF",
  "description": "...",
  "nodes": [...],
  "edges": [...],
  "is_valid": true,
  "created_at": "2026-01-12T10:00:00",
  "updated_at": "2026-01-12T10:00:00"
}
```

#### GET /workflows/
**Description**: List all workflows  

#### GET /workflows/{id}
**Description**: Get specific workflow  

#### PUT /workflows/{id}
**Description**: Update workflow  

#### DELETE /workflows/{id}
**Description**: Delete workflow  

#### POST /workflows/{id}/validate
**Description**: Validate workflow structure  
**Response**:
```json
{
  "workflow_id": "uuid",
  "is_valid": true,
  "message": "Workflow is valid"
}
```

---

### Chat Execution

#### POST /chat/execute
**Description**: Execute workflow with a query  
**Request Body**:
```json
{
  "workflow_id": "uuid",
  "query": "What is the main topic of the document?",
  "session_id": "uuid"  // optional
}
```
**Response**:
```json
{
  "session_id": "uuid",
  "user_message": {
    "id": "uuid",
    "role": "user",
    "content": "What is...",
    "created_at": "..."
  },
  "assistant_message": {
    "id": "uuid",
    "role": "assistant",
    "content": "The main topic is...",
    "created_at": "..."
  }
}
```

#### GET /chat/sessions/{id}
**Description**: Get chat session with messages  
**Response**:
```json
{
  "id": "uuid",
  "workflow_id": "uuid",
  "created_at": "...",
  "messages": [...]
}
```

---

### Health Check

#### GET /health/
**Description**: Check system health  
**Response**:
```json
{
  "status": "healthy",
  "database": "healthy",
  "vector_store": "healthy"
}
```

---

## 2. Workflow Validation Algorithm

```python
def validate_workflow(nodes, edges):
    """
    Validates workflow structure:
    1. Check all nodes have recognized types
    2. Validate edges connect valid nodes
    3. Detect cycles using DFS
    4. Ensure Input and Output components exist
    5. Verify required configurations
    
    Returns: (is_valid, error_message)
    """
    
    # Check node types
    valid_types = {'userquery', 'knowledgebase', 'llmengine', 'output'}
    for node in nodes:
        if node['type'] not in valid_types:
            return False, f"Invalid type: {node['type']}"
    
    # Build adjacency list
    graph = build_graph(edges)
    
    # Detect cycles using DFS
    if has_cycle(graph):
        return False, "Workflow contains a cycle"
    
    # Check for Input/Output
    has_input = any(n['type'] in ['userquery', 'input'] for n in nodes)
    has_output = any(n['type'] == 'output' for n in nodes)
    
    if not has_input or not has_output:
        return False, "Must have Input and Output components"
    
    return True, "Workflow is valid"
```

## 3. Workflow Execution Algorithm

```python
async def execute_workflow(workflow, query):
    """
    Executes workflow in topological order:
    1. Validate workflow
    2. Get execution order (topological sort)
    3. Initialize all component instances
    4. Execute each component sequentially
    5. Pass output to next component
    6. Return final result
    """
    
    # Validate
    is_valid, msg = validate_workflow(workflow.nodes, workflow.edges)
    if not is_valid:
        raise ValidationError(msg)
    
    # Get execution order
    execution_order = topological_sort(workflow.nodes, workflow.edges)
    
    # Initialize components
    components = {}
    for node_id in execution_order:
        node = get_node_by_id(node_id)
        components[node_id] = create_component(node_id, node.data)
    
    # Execute in order
    current_data = {"query": query}
    for node_id in execution_order:
        component = components[node_id]
        output = await component.execute(current_data)
        current_data = output
    
    # Extract final response
    return current_data.get("response", current_data)
```

---

# Deployment Architecture

## 1. Docker Compose Services

```yaml
services:
  frontend:
    - Build: Multi-stage (Node build + Nginx serve)
    - Port: 80
    - Depends on: backend
    
  backend:
    - Build: Python 3.11 with dependencies
    - Port: 8000
    - Depends on: postgres
    - Volumes: uploads, chroma_data
    
  postgres:
    - Image: postgres:16-alpine
    - Port: 5432
    - Volume: postgres_data
    - Health check: pg_isready
    
  chromadb:
    - Embedded in backend (not separate container)
    - Persisted in volume
```

## 2. Network Architecture

```
Internet
   │
   ↓
┌──────────────┐
│  Port 80     │
│  Nginx       │
│  (Frontend)  │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  Port 8000   │
│  FastAPI     │
│  (Backend)   │
└──────┬───────┘
       │
   ┌───┴───┐
   ↓       ↓
┌──────┐ ┌────────┐
│ PG   │ │ChromaDB│
│:5432 │ │Embedded│
└──────┘ └────────┘
```

## 3. Security Considerations

- API keys stored in `.env` files (not in git)
- CORS configured for specific origins
- SQL injection prevention via SQLAlchemy ORM
- Input validation using Pydantic
- File upload validation (PDF only)
- Database credentials in environment variables
- No hardcoded secrets in codebase

## 4. Scalability Considerations

**Current Limitations**:
- Single instance deployment
- Embedded ChromaDB
- Synchronous document processing

**Future Improvements**:
- Redis for distributed caching
- Separate ChromaDB server
- Background task queue (Celery/Redis)
- Load balancer for multiple backend instances
- CDN for frontend assets
- Database read replicas

---

# Summary

## Key Design Decisions

1. **Modular Component Architecture**: Each workflow component is independent and implements a common interface
2. **Graph-Based Workflow**: Workflows stored as nodes + edges, executed via topological sort
3. **JSONB Storage**: React Flow graphs stored directly in PostgreSQL as JSONB
4. **Embedded Vector Store**: ChromaDB runs embedded for simplicity
5. **Docker-First**: All services containerized for consistent deployment

## Performance Characteristics

- **Document Processing**: ~5-10 seconds for 50-page PDF
- **Vector Search**: <100ms for similarity search
- **LLM Response**: 2-5 seconds depending on OpenAI API
- **Workflow Execution**: Sum of component execution times + overhead (~5-10s typically)

## Future Enhancements

1. Add user authentication (JWT)
2. Implement workflow templates
3. Add more component types (API calls, transformations)
4. Real-time collaboration
5. Workflow versioning
6. Analytics dashboard
7. Kubernetes deployment
8. Monitoring with Prometheus/Grafana

---

**End of Document**

For implementation details, refer to:
- Source Code: https://github.com/krayush7707/PlanetAiAssignment
- README: https://github.com/krayush7707/PlanetAiAssignment/blob/main/README.md
- API Documentation: http://localhost:8000/docs (when running)
