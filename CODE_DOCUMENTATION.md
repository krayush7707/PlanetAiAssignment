# GenAI Stack - Complete Source Code Documentation

**Project**: No-Code/Low-Code Workflow Builder  
**Author**: Ayush Kumar (krayush7707)  
**Repository**: https://github.com/krayush7707/PlanetAiAssignment  
**Last Updated**: January 2026

---

## Table of Contents

1. [Code Architecture Overview](#code-architecture-overview)
2. [Backend Documentation](#backend-documentation)
3. [Frontend Documentation](#frontend-documentation)
4. [Key Interactions & Data Flow](#key-interactions--data-flow)
5. [Configuration & Setup](#configuration--setup)
6. [Testing & Debugging](#testing--debugging)

---

# Code Architecture Overview

## Project Structure

```
PlanetAiAssignment/
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   ├── components/        # Workflow component implementations
│   │   ├── database/          # Database models & schemas
│   │   ├── vector_store/      # ChromaDB integration
│   │   └── workflow/          # Workflow engine
│   ├── main.py               # Application entry point
│   ├── config.py             # Configuration management
│   └── requirements.txt      # Python dependencies
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── services/          # API client
│   │   ├── store/             # State management
│   │   ├── App.jsx           # Main application
│   │   └── index.css         # Global styles
│   ├── package.json          # Node dependencies
│   └── Dockerfile            # Frontend container
│
├── docker-compose.yml         # Service orchestration
└── README.md                 # Project documentation
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React 19 + Vite | UI Framework |
| UI Components | React Flow | Workflow visualization |
| State | Zustand | Client state management |
| Styling | TailwindCSS | UI styling |
| Backend | FastAPI | REST API |
| Database | PostgreSQL 16 | Relational data |
| Vector DB | ChromaDB | Embeddings storage |
| ORM | SQLAlchemy 2.0 | Database abstraction |
| Validation | Pydantic | Data validation |
| LLM | OpenAI GPT-4 | Language model |
| Search | SerpAPI | Web search |
| Containers | Docker Compose | Deployment |

---

# Backend Documentation

## 1. Application Entry Point

### `main.py`

**Location**: `backend/main.py`  
**Purpose**: FastAPI application initialization and configuration

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="GenAI Stack API",
    description="No-Code/Low-Code Workflow Builder API",
    version="1.0.0"
)
```

**Key Responsibilities**:
- Initialize FastAPI application
- Configure CORS middleware for cross-origin requests
- Include API routers (documents, workflows, chat, health)
- Database initialization on startup
- Logging configuration

**Startup Flow**:
1. Import configuration from `config.py`
2. Set up CORS with allowed origins
3. Register API routers
4. Initialize database tables
5. Start uvicorn server on port 8000

**Important Code Sections**:

```python
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # From config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Registration
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(workflows.router)
app.include_router(chat.router)

# Database Initialization
@app.on_event("startup")
async def startup_event():
    init_db()  # Creates all tables
```

---

## 2. Configuration Management

### `config.py`

**Location**: `backend/config.py`  
**Purpose**: Centralized configuration using Pydantic Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    serpapi_api_key: str
    chroma_persist_dir: str
    
    class Config:
        env_file = ".env"
```

**Configuration Sources**:
1. Environment variables
2. `.env` file
3. Default values in code

**Usage Throughout Application**:
```python
from config import settings

# Access configuration
openai_client = OpenAI(api_key=settings.openai_api_key)
```

---

## 3. Database Layer

### `app/database/models.py`

**Location**: `backend/app/database/models.py`  
**Purpose**: SQLAlchemy ORM models

#### Document Model

```python
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    processed = Column(Boolean, default=False)
    collection_name = Column(String, nullable=True)
```

**Purpose**: Stores metadata about uploaded PDF documents

**Key Fields**:
- `id`: Unique identifier (UUID)
- `filename`: Original filename
- `file_path`: Path to stored file
- `processed`: Whether document has been embedded
- `collection_name`: Reference to ChromaDB collection

#### Workflow Model

```python
class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    nodes = Column(JSON, nullable=False)  # React Flow nodes
    edges = Column(JSON, nullable=False)  # React Flow edges
    is_valid = Column(Boolean, default=False)
```

**Purpose**: Stores workflow definitions

**Key Fields**:
- `nodes`: JSONB storing React Flow node data
- `edges`: JSONB storing connections between nodes
- `is_valid`: Cached validation result

#### ChatSession & ChatMessage Models

```python
class ChatSession(Base):
    workflow_id = Column(String, ForeignKey("workflows.id"))
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
```

**Purpose**: Store chat conversation history

**Relationships**:
- Workflow → ChatSession (1:N)
- ChatSession → ChatMessage (1:N)

---

### `app/database/connection.py`

**Location**: `backend/app/database/connection.py`  
**Purpose**: Database connection and session management

```python
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Usage in API Endpoints**:
```python
@router.get("/workflows/")
async def list_workflows(db: Session = Depends(get_db)):
    workflows = db.query(Workflow).all()
    return {"workflows": workflows}
```

**Key Functions**:
- `get_db()`: FastAPI dependency for database sessions
- `init_db()`: Creates all tables on startup

---

### `app/database/schemas.py`

**Location**: `backend/app/database/schemas.py`  
**Purpose**: Pydantic models for request/response validation

**Example Schema**:
```python
class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

class WorkflowResponse(BaseModel):
    id: str
    name: str
    nodes: List[Dict[str, Any]]
    is_valid: bool
    
    class Config:
        from_attributes = True  # Allow ORM objects
```

**Purpose**: 
- Validate incoming API requests
- Serialize database objects to JSON
- Auto-generate OpenAPI documentation

---

## 4. Vector Store Integration

### `app/vector_store/chromadb_client.py`

**Location**: `backend/app/vector_store/chromadb_client.py`  
**Purpose**: ChromaDB wrapper for vector operations

```python
class ChromaDBClient:
    def __init__(self):
        self.client = chromadb.Client(
            Settings(persist_directory=settings.chroma_persist_dir)
        )
    
    def create_collection(self, collection_name: str):
        return self.client.get_or_create_collection(collection_name)
    
    def add_embeddings(self, collection_name, embeddings, documents, ...):
        collection = self.create_collection(collection_name)
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query_embeddings(self, collection_name, query_embedding, n_results=5):
        collection = self.client.get_collection(collection_name)
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
```

**Key Methods**:
1. `create_collection()`: Initialize vector collection
2. `add_embeddings()`: Store document embeddings
3. `query_embeddings()`: Semantic search
4. `delete_collection()`: Cleanup

**Usage in Components**:
```python
from app.vector_store.chromadb_client import chroma_client

# Store embeddings
chroma_client.add_embeddings(
    collection_name="doc_123",
    embeddings=embedding_vectors,
    documents=text_chunks,
    metadatas=metadata_list,
    ids=chunk_ids
)

# Query similar documents
results = chroma_client.query_embeddings(
    collection_name="doc_123",
    query_embedding=query_vector,
    n_results=5
)
```

---

## 5. Workflow Components

### Base Component (`app/components/base.py`)

**Location**: `backend/app/components/base.py`  
**Purpose**: Abstract base class for all workflow components

```python
class BaseComponent(ABC):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.component_type = config.get("type")
    
    @abstractmethod
    async def execute(self, input_data: Optional[Any]) -> Any:
        """Execute component logic"""
        pass
    
    def validate_config(self) -> bool:
        """Validate component configuration"""
        return True
```

**Design Pattern**: Template Method Pattern
- Base class defines the interface
- Subclasses implement specific behavior
- Common functionality in base class

---

### User Query Component (`app/components/user_query.py`)

**Location**: `backend/app/components/user_query.py`  
**Purpose**: Entry point for user queries

```python
class UserQueryComponent(BaseComponent):
    async def execute(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        # Extract query from various input formats
        if isinstance(input_data, str):
            query = input_data
        elif isinstance(input_data, dict):
            query = input_data.get("query", "")
        
        return {
            "query": query,
            "component_type": "user_query",
            "node_id": self.node_id
        }
```

**Responsibilities**:
- Accept user input
- Normalize query format
- Pass to next component

**Input**: String or dict with "query" key  
**Output**: Dict with standardized query

---

### Knowledge Base Component (`app/components/knowledgebase.py`)

**Location**: `backend/app/components/knowledgebase.py`  
**Purpose**: Document processing and RAG (Retrieval Augmented Generation)

```python
class KnowledgeBaseComponent(BaseComponent):
    def __init__(self, node_id, config):
        super().__init__(node_id, config)
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.collection_name = config.get("collection_name")
        self.chunk_size = config.get("chunk_size", 1000)
        self.chunk_overlap = config.get("chunk_overlap", 200)
        self.top_k = config.get("top_k", 5)
    
    async def execute(self, input_data) -> Dict[str, Any]:
        query = extract_query(input_data)
        
        # Generate query embedding
        query_embedding = await self._generate_embedding(query)
        
        # Retrieve relevant chunks
        results = chroma_client.query_embeddings(
            self.collection_name,
            query_embedding,
            n_results=self.top_k
        )
        
        # Extract and combine documents
        documents = results["documents"][0]
        context = "\n\n".join(documents)
        
        return {
            "query": query,
            "context": context,
            "documents": documents
        }
    
    async def process_document(self, file_path, filename):
        # 1. Extract text from PDF
        text = self._extract_text_from_pdf(file_path)
        
        # 2. Chunk text
        chunks = self._chunk_text(text)
        
        # 3. Generate embeddings for each chunk
        embeddings = []
        for chunk in chunks:
            embedding = await self._generate_embedding(chunk)
            embeddings.append(embedding)
        
        # 4. Store in ChromaDB
        chroma_client.add_embeddings(
            collection_name=self.collection_name,
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"filename": filename, "chunk_idx": i} 
                      for i in range(len(chunks))],
            ids=[f"{self.collection_name}_{i}" for i in range(len(chunks))]
        )
```

**Key Methods**:

1. **`_extract_text_from_pdf()`**: Uses PyMuPDF to extract text
   ```python
   def _extract_text_from_pdf(self, file_path):
       doc = fitz.open(file_path)
       text = ""
       for page in doc:
           text += page.get_text()
       return text
   ```

2. **`_chunk_text()`**: Splits text with overlap
   ```python
   def _chunk_text(self, text):
       chunks = []
       start = 0
       while start < len(text):
           end = start + self.chunk_size
           chunks.append(text[start:end])
           start += self.chunk_size - self.chunk_overlap
       return chunks
   ```

3. **`_generate_embedding()`**: Calls OpenAI Embeddings API
   ```python
   async def _generate_embedding(self, text):
       response = self.openai_client.embeddings.create(
           model="text-embedding-3-small",
           input=text
       )
       return response.data[0].embedding
   ```

**Data Flow**:
```
PDF File → Text Extraction → Chunking → Embeddings → ChromaDB
Query → Query Embedding → Vector Search → Retrieved Context
```

---

### LLM Engine Component (`app/components/llm_engine.py`)

**Location**: `backend/app/components/llm_engine.py`  
**Purpose**: LLM integration with GPT and web search

```python
class LLMEngineComponent(BaseComponent):
    def __init__(self, node_id, config):
        super().__init__(node_id, config)
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.model = config.get("model", "gpt-4o-mini")
        self.temperature = config.get("temperature", 0.7)
        self.custom_prompt = config.get("custom_prompt", "")
        self.use_web_search = config.get("use_web_search", False)
    
    async def execute(self, input_data) -> Dict[str, Any]:
        query = input_data.get("query", "")
        context = input_data.get("context", "")
        
        # Optional web search
        web_context = ""
        if self.use_web_search:
            web_context = await self._perform_web_search(query)
        
        # Build prompt
        prompt = self._build_prompt(query, context, web_context)
        
        # Call GPT
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        
        generated_text = response.choices[0].message.content
        
        return {
            "response": generated_text,
            "query": query,
            "context_used": bool(context)
        }
    
    def _build_prompt(self, query, context, web_context):
        if self.custom_prompt:
            # Replace placeholders
            prompt = self.custom_prompt
            prompt = prompt.replace("{query}", query)
            prompt = prompt.replace("{context}", context)
            return prompt
        
        # Default prompt template
        parts = []
        if context:
            parts.append(f"Context from documents:\n{context}\n")
        if web_context:
            parts.append(f"Web search results:\n{web_context}\n")
        parts.append(f"User query: {query}")
        
        return "\n".join(parts)
    
    async def _perform_web_search(self, query):
        search = GoogleSearch({
            "q": query,
            "api_key": settings.serpapi_api_key,
            "num": 5
        })
        results = search.get_dict()
        
        # Format results
        formatted = []
        for result in results.get("organic_results", [])[:5]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            formatted.append(f"{title}\n{snippet}")
        
        return "\n\n".join(formatted)
```

**Prompt Template System**:
- Supports custom prompts with placeholders
- Placeholders: `{query}`, `{context}`, `{User Query}`, `{CONTEXT}`
- Falls back to default template if not provided

**Web Search Integration**:
- Uses SerpAPI for Google search
- Fetches top 5 organic results
- Extracts title and snippet
- Merges with prompt

---

### Output Component (`app/components/output.py`)

**Location**: `backend/app/components/output.py`  
**Purpose**: Format final output

```python
class OutputComponent(BaseComponent):
    def __init__(self, node_id, config):
        super().__init__(node_id, config)
        self.output_format = config.get("output_format", "text")
    
    async def execute(self, input_data) -> Dict[str, Any]:
        # Extract response from previous component
        if isinstance(input_data, dict):
            response = input_data.get("response", str(input_data))
        else:
            response = str(input_data)
        
        return {
            "output": response,
            "response": response,
            "component_type": "output"
        }
```

**Simple but Essential**:
- Ensures consistent output format
- Last step in workflow execution
- Could be extended for different formats (JSON, XML, etc.)

---

### Component Factory (`app/components/__init__.py`)

**Location**: `backend/app/components/__init__.py`  
**Purpose**: Create component instances based on type

```python
COMPONENT_REGISTRY = {
    "userquery": UserQueryComponent,
    "user_query": UserQueryComponent,
    "knowledgebase": KnowledgeBaseComponent,
    "knowledge_base": KnowledgeBaseComponent,
    "llmengine": LLMEngineComponent,
    "llm_engine": LLMEngineComponent,
    "output": OutputComponent
}

def create_component(node_id: str, node_data: Dict) -> BaseComponent:
    component_type = node_data.get("type", "").lower()
    
    if component_type not in COMPONENT_REGISTRY:
        raise ValueError(f"Unknown component type: {component_type}")
    
    component_class = COMPONENT_REGISTRY[component_type]
    return component_class(node_id, node_data)
```

**Factory Pattern Benefits**:
- Centralized component creation
- Easy to add new component types
- Type validation

---

## 6. Workflow Engine

### Workflow Validator (`app/workflow/validator.py`)

**Location**: `backend/app/workflow/validator.py`  
**Purpose**: Validate workflow structure before execution

```python
class WorkflowValidator:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.node_map = {node["id"]: node for node in nodes}
    
    def validate(self) -> Tuple[bool, str]:
        # 1. Check nodes exist
        if not self.nodes:
            return False, "Workflow must have at least one component"
        
        # 2. Validate node types
        valid, msg = self._validate_node_types()
        if not valid:
            return False, msg
        
        # 3. Validate connections
        valid, msg = self._validate_connections()
        if not valid:
            return False, msg
        
        # 4. Check for cycles
        valid, msg = self._check_for_cycles()
        if not valid:
            return False, msg
        
        # 5. Validate workflow flow
        valid, msg = self._validate_workflow_flow()
        if not valid:
            return False, msg
        
        return True, "Workflow is valid"
```

**Validation Steps**:

1. **Node Type Validation**:
   ```python
   def _validate_node_types(self):
       valid_types = {'userquery', 'knowledgebase', 'llmengine', 'output'}
       for node in self.nodes:
           node_type = node.get("data", {}).get("type", "").lower()
           if node_type not in valid_types:
               return False, f"Invalid type: {node_type}"
       return True, ""
   ```

2. **Cycle Detection (DFS)**:
   ```python
   def _check_for_cycles(self):
       graph = {node["id"]: [] for node in self.nodes}
       for edge in self.edges:
           graph[edge["source"]].append(edge["target"])
       
       visited = set()
       rec_stack = set()
       
       def has_cycle(node_id):
           visited.add(node_id)
           rec_stack.add(node_id)
           
           for neighbor in graph[node_id]:
               if neighbor not in visited:
                   if has_cycle(neighbor):
                       return True
               elif neighbor in rec_stack:
                   return True
           
           rec_stack.remove(node_id)
           return False
       
       for node_id in graph:
           if node_id not in visited:
               if has_cycle(node_id):
                   return False, "Workflow contains a cycle"
       
       return True, ""
   ```

3. **Topological Sort** (for execution order):
   ```python
   def get_execution_order(self):
       graph = {node["id"]: [] for node in self.nodes}
       in_degree = {node["id"]: 0 for node in self.nodes}
       
       for edge in self.edges:
           graph[edge["source"]].append(edge["target"])
           in_degree[edge["target"]] += 1
       
       # Kahn's algorithm
       queue = [n for n, d in in_degree.items() if d == 0]
       order = []
       
       while queue:
           node_id = queue.pop(0)
           order.append(node_id)
           
           for neighbor in graph[node_id]:
               in_degree[neighbor] -= 1
               if in_degree[neighbor] == 0:
                   queue.append(neighbor)
       
       return order
   ```

---

### Workflow Executor (`app/workflow/executor.py`)

**Location**: `backend/app/workflow/executor.py`  
**Purpose**: Execute validated workflows

```python
class WorkflowExecutor:
    def __init__(self, workflow_data):
        self.workflow_id = workflow_data.get("id")
        self.nodes = workflow_data.get("nodes", [])
        self.edges = workflow_data.get("edges", [])
        self.validator = WorkflowValidator(self.nodes, self.edges)
        self.components = {}
        self.execution_log = []
    
    async def execute(self, query: str) -> Dict[str, Any]:
        # 1. Validate workflow
        is_valid, error_msg = self.validator.validate()
        if not is_valid:
            return {
                "success": False,
                "error": error_msg
            }
        
        # 2. Get execution order
        execution_order = self.validator.get_execution_order()
        
        # 3. Initialize components
        self._initialize_components()
        
        # 4. Execute components in order
        try:
            current_data = {"query": query}
            
            for node_id in execution_order:
                component = self.components[node_id]
                
                # Log execution
                self._log_execution(node_id, "started", current_data)
                
                # Execute
                output = await component.execute(current_data)
                
                # Log completion
                self._log_execution(node_id, "completed", output)
                
                # Pass to next component
                current_data = output
            
            # Extract final response
            final_output = current_data.get("response", current_data.get("output"))
            
            return {
                "success": True,
                "output": final_output,
                "execution_log": self.execution_log
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_log": self.execution_log
            }
    
    def _initialize_components(self):
        for node in self.nodes:
            node_id = node["id"]
            node_data = node.get("data", {})
            
            component = create_component(node_id, node_data)
            self.components[node_id] = component
```

**Execution Flow**:
```
1. Validate workflow structure
2. Get topological order of nodes
3. Initialize all component instances
4. For each node in order:
   a. Log start
   b. Execute component
   c. Log completion
   d. Pass output to next
5. Return final output
```

---

## 7. API Endpoints

### Documents API (`app/api/documents.py`)

**Location**: `backend/app/api/documents.py`

**Endpoints**:

1. **POST /documents/upload**
   ```python
   @router.post("/upload", response_model=DocumentUploadResponse)
   async def upload_document(
       file: UploadFile = File(...),
       db: Session = Depends(get_db)
   ):
       # 1. Validate file type
       if not file.filename.endswith('.pdf'):
           raise HTTPException(400, "Only PDF files supported")
       
       # 2. Save file
       file_id = str(uuid.uuid4())
       file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
       
       async with aiofiles.open(file_path, 'wb') as f:
           content = await file.read()
           await f.write(content)
       
       # 3. Create database record
       doc = Document(
           id=file_id,
           filename=file.filename,
           file_path=file_path,
           file_size=len(content)
       )
       db.add(doc)
       db.commit()
       
       # 4. Process document (extract, embed, store)
       kb_component = KnowledgeBaseComponent(
           node_id=file_id,
           config={"collection_name": f"doc_{file_id}"}
       )
       result = await kb_component.process_document(file_path, file.filename)
       
       # 5. Update document status
       if result.get("success"):
           doc.processed = True
           doc.chunk_count = result.get("chunk_count")
           doc.collection_name = f"doc_{file_id}"
           db.commit()
       
       return doc
   ```

2. **GET /documents/**
   ```python
   @router.get("/", response_model=DocumentList)
   async def list_documents(db: Session = Depends(get_db)):
       documents = db.query(Document).all()
       return {"documents": documents}
   ```

3. **DELETE /documents/{id}**
   ```python
   @router.delete("/{document_id}")
   async def delete_document(document_id: str, db: Session = Depends(get_db)):
       doc = db.query(Document).filter(Document.id == document_id).first()
       if not doc:
           raise HTTPException(404, "Document not found")
       
       # Delete file
       if os.path.exists(doc.file_path):
           os.remove(doc.file_path)
       
       # Delete from database
       db.delete(doc)
       db.commit()
       
       return {"message": "Document deleted successfully"}
   ```

---

### Workflows API (`app/api/workflows.py`)

**Location**: `backend/app/api/workflows.py`

**Key Endpoints**:

1. **POST /workflows/** - Create workflow
2. **GET /workflows/** - List all workflows
3. **GET /workflows/{id}** - Get specific workflow
4. **PUT /workflows/{id}** - Update workflow
5. **DELETE /workflows/{id}** - Delete workflow
6. **POST /workflows/{id}/validate** - Validate workflow

**Example - Create Workflow**:
```python
@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    # Validate if nodes/edges provided
    is_valid = False
    if workflow_data.nodes and workflow_data.edges:
        validator = WorkflowValidator(workflow_data.nodes, workflow_data.edges)
        is_valid, _ = validator.validate()
    
    workflow = Workflow(
        name=workflow_data.name,
        description=workflow_data.description,
        nodes=workflow_data.nodes,
        edges=workflow_data.edges,
        is_valid=is_valid
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return workflow
```

---

### Chat API (`app/api/chat.py`)

**Location**: `backend/app/api/chat.py`

**POST /chat/execute**:
```python
@router.post("/execute", response_model=ChatExecuteResponse)
async def execute_chat(
    request: ChatExecuteRequest,
    db: Session = Depends(get_db)
):
    # 1. Get workflow
    workflow = db.query(Workflow).filter(Workflow.id == request.workflow_id).first()
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    # 2. Check if valid
    if not workflow.is_valid:
        raise HTTPException(400, "Workflow is not valid")
    
    # 3. Get or create session
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    else:
        session = ChatSession(workflow_id=request.workflow_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # 4. Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    db.commit()
    
    # 5. Execute workflow
    workflow_data = {
        "id": workflow.id,
        "nodes": workflow.nodes,
        "edges": workflow.edges
    }
    executor = WorkflowExecutor(workflow_data)
    result = await executor.execute(request.query)
    
    if not result.get("success"):
        raise HTTPException(500, result.get("error"))
    
    # 6. Save assistant message
    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result.get("output")
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    return ChatExecuteResponse(
        session_id=session.id,
        user_message=user_message,
        assistant_message=assistant_message
    )
```

---

# Frontend Documentation

## 1. Application Structure

### `src/App.jsx`

**Location**: `frontend/src/App.jsx`  
**Purpose**: Main application component with routing

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<MyStacksPage />} />
          <Route path="/workflow/:id" element={<WorkflowBuilderPage />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}
```

**Key Components**:
1. **MyStacksPage** - Workflow list and creation
2. **WorkflowBuilderPage** - Visual workflow editor

---

## 2. Pages

### My Stacks Page

**Component**: `MyStacksPage` in `App.jsx`

**Responsibilities**:
- List all saved workflows
- Create new workflows
- Navigate to workflow builder

**Key State**:
```jsx
const [showModal, setShowModal] = useState(false);
const [formData, setFormData] = useState({ name: '', description: '' });
```

**Data Fetching**:
```jsx
const { data: workflowsData, refetch } = useQuery({
  queryKey: ['workflows'],
  queryFn: async () => {
    const res = await workflowAPI.list();
    return res.data.workflows;
  },
});
```

**Workflow Creation**:
```jsx
const createMutation = useMutation({
  mutationFn: (data) => workflowAPI.create(data),
  onSuccess: (response) => {
    refetch();
    setShowModal(false);
    navigate(`/workflow/${response.data.id}`);
  },
});
```

---

### Workflow Builder Page

**Component**: `WorkflowBuilderPage` in `App.jsx`

**Responsibilities**:
- Visual workflow canvas
- Drag-and-drop components
- Component configuration
- Save workflows
- Open chat interface

**State Management**:
```jsx
// React Flow state
const [nodes, setNodes, onNodesChange] = useNodesState([]);
const [edges, setEdges, onEdgesChange] = useEdgesState([]);

// UI state
const [selectedNode, setSelectedNode] = useState(null);
const [chatOpen, setChatOpen] = useState(false);
```

**Load Workflow**:
```jsx
const { data: workflow } = useQuery({
  queryKey: ['workflow', id],
  queryFn: async () => {
    const res = await workflowAPI.get(id);
    return res.data;
  },
});

useEffect(() => {
  if (workflow) {
    setNodes(workflow.nodes || []);
    setEdges(workflow.edges || []);
  }
}, [workflow]);
```

**Drag & Drop**:
```jsx
const onDragStart = (event, nodeType) => {
  event.dataTransfer.setData('application/reactflow', nodeType);
};

const onDrop = (event) => {
  event.preventDefault();
  const type = event.dataTransfer.getData('application/reactflow');
  const position = { 
    x: event.clientX - 300, 
    y: event.clientY - 100 
  };
  
  const newNode = {
    id: `${type}-${Date.now()}`,
    type: 'default',
    data: { label: type, type },
    position,
  };
  
  setNodes((nds) => nds.concat(newNode));
};
```

**Connect Nodes**:
```jsx
const onConnect = (params) => {
  setEdges((eds) => addEdge(params, eds));
};
```

**Save Workflow**:
```jsx
const updateMutation = useMutation({
  mutationFn: (data) => workflowAPI.update(id, data),
});

const handleSave = () => {
  updateMutation.mutate({ nodes, edges });
};
```

---

## 3. Components

### Chat Modal

**Component**: `ChatModal` in `App.jsx`

**Purpose**: Interactive chat interface

**State**:
```jsx
const [query, setQuery] = useState('');
const [messages, setMessages] = useState([]);
const [sessionId, setSessionId] = useState(null);
const [loading, setLoading] = useState(false);
```

**Send Message**:
```jsx
const handleSend = async () => {
  if (!query.trim()) return;
  
  // Add user message to UI
  setMessages([...messages, { role: 'user', content: query }]);
  setQuery('');
  setLoading(true);
  
  try {
    // Call API
    const res = await chatAPI.execute({
      workflow_id: workflowId,
      query,
      session_id: sessionId
    });
    
    // Update session ID
    setSessionId(res.data.session_id);
    
    // Add assistant message
    setMessages((msgs) => [
      ...msgs,
      { role: 'assistant', content: res.data.assistant_message.content }
    ]);
  } catch (error) {
    setMessages((msgs) => [
      ...msgs,
      { role: 'assistant', content: 'Error: ' + error.message }
    ]);
  }
  
  setLoading(false);
};
```

**Message Display**:
```jsx
{messages.map((msg, idx) => (
  <div key={idx} className="flex gap-3">
    <div className={`w-8 h-8 rounded-full ${
      msg.role === 'user' ? 'bg-blue-100' : 'bg-green-100'
    }`}>
      {msg.role === 'user' ? 'U' : <Sparkles />}
    </div>
    <div className={`p-3 rounded-lg ${
      msg.role === 'user' ? 'bg-blue-50' : 'bg-white border'
    }`}>
      <p>{msg.content}</p>
    </div>
  </div>
))}
```

---

## 4. Services

### API Client (`src/services/api.js`)

**Location**: `frontend/src/services/api.js`

```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Workflows
export const workflowAPI = {
  list: () => api.get('/workflows/'),
  get: (id) => api.get(`/workflows/${id}`),
  create: (data) => api.post('/workflows/', data),
  update: (id, data) => api.put(`/workflows/${id}`, data),
  delete: (id) => api.delete(`/workflows/${id}`),
};

// Documents
export const documentAPI = {
  list: () => api.get('/documents/'),
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id) => api.delete(`/documents/${id}`),
};

// Chat
export const chatAPI = {
  execute: (data) => api.post('/chat/execute', data),
  getSession: (sessionId) => api.get(`/chat/sessions/${sessionId}`),
};
```

---

## 5. State Management

### `src/store/workflowStore.js`

**Location**: `frontend/src/store/workflowStore.js`

```javascript
import { create } from 'zustand';

export const useWorkflowStore = create((set, get) => ({
  // State
  currentWorkflow: null,
  nodes: [],
  edges: [],
  selectedNode: null,
  
  // Actions
  setWorkflow: (workflow) => set({
    currentWorkflow: workflow,
    nodes: workflow?.nodes || [],
    edges: workflow?.edges || [],
  }),
  
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setSelectedNode: (node) => set({ selectedNode: node }),
  
  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node],
  })),
  
  updateNodeData: (nodeId, data) => set((state) => ({
    nodes: state.nodes.map((node) =>
      node.id === nodeId 
        ? { ...node, data: { ...node.data, ...data } } 
        : node
    ),
  })),
  
  removeNode: (nodeId) => set((state) => ({
    nodes: state.nodes.filter((node) => node.id !== nodeId),
    edges: state.edges.filter(
      (edge) => edge.source !== nodeId && edge.target !== nodeId
    ),
  })),
  
  clearWorkflow: () => set({
    currentWorkflow: null,
    nodes: [],
    edges: [],
    selectedNode: null,
  }),
}));
```

**Usage in Components**:
```jsx
import { useWorkflowStore } from './store/workflowStore';

function MyComponent() {
  const { nodes, setNodes, addNode } = useWorkflowStore();
  
  const handleAddNode = () => {
    addNode({
      id: 'new-node',
      type: 'default',
      data: { label: 'New Node' },
      position: { x: 100, y: 100 },
    });
  };
}
```

---

## 6. Styling

### `src/index.css`

**Location**: `frontend/src/index.css`

**TailwindCSS Configuration**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply bg-primary hover:bg-primary-hover text-white 
           font-medium px-6 py-2.5 rounded-lg 
           transition-colors duration-200;
  }
  
  .btn-secondary {
    @apply bg-secondary hover:bg-secondary-hover text-white 
           font-medium px-6 py-2.5 rounded-lg 
           transition-colors duration-200;
  }
  
  .card {
    @apply bg-white rounded-xl border border-gray-200 p-6 
           hover:shadow-md transition-shadow duration-200;
  }
  
  .input-field {
    @apply w-full px-4 py-2.5 border border-gray-300 rounded-lg 
           focus:outline-none focus:ring-2 focus:ring-primary;
  }
}
```

**Custom Colors** (tailwind.config.js):
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4CAF50',
          hover: '#43A047',
        },
        secondary: {
          DEFAULT: '#2196F3',
          hover: '#1976D2',
        },
      },
    },
  },
}
```

---

# Key Interactions & Data Flow

## 1. Document Upload Flow

```
User → Frontend → Backend API → File System
                             ↓
                      PyMuPDF (Extract Text)
                             ↓
                      Text Chunking
                             ↓
                      OpenAI Embeddings API
                             ↓
                      ChromaDB (Store Vectors)
                             ↓
                      PostgreSQL (Metadata)
                             ↓
                      Response to Frontend
```

**Code Trace**:
1. User uploads PDF in frontend
2. `documentAPI.upload(file)` sends FormData to backend
3. `/documents/upload` endpoint receives file
4. File saved to disk (`UPLOAD_DIR/uploads`)
5. `KnowledgeBaseComponent.process_document()` called
6. `_extract_text_from_pdf()` extracts text using PyMuPDF
7. `_chunk_text()` splits into overlapping chunks
8. `_generate_embedding()` calls OpenAI for each chunk
9. `chroma_client.add_embeddings()` stores vectors in ChromaDB
10. Document metadata saved to PostgreSQL
11. Response sent back to frontend

## 2. Workflow Creation Flow

```
User → Frontend (Create Modal)
         ↓
    Form Submission
         ↓
    workflowAPI.create({name, description})
         ↓
    Backend API (POST /workflows/)
         ↓
    Create Workflow in PostgreSQL
         ↓
    Return Workflow ID
         ↓
    Navigate to /workflow/{id}
```

## 3. Chat Execution Flow

```
User Types Query → Chat Modal
                      ↓
                 Send to Backend
                      ↓
              Get Workflow from DB
                      ↓
              Validate Workflow
                      ↓
              Execute Components:
                      ↓
              1. UserQuery (normalize input)
                      ↓
              2. KnowledgeBase (retrieve context)
                 ├→ Query → OpenAI Embedding
                 └→ Vector Search → ChromaDB
                      ↓
              3. LLMEngine (generate response)
                 ├→ Build Prompt (query + context)
                 ├→ Optional: Web Search (SerpAPI)
                 └→ Call GPT API
                      ↓
              4. Output (format result)
                      ↓
              Save Messages to PostgreSQL
                      ↓
              Return to Frontend
                      ↓
              Display in Chat
```

**Detailed Code Path**:

1. **Frontend**: User types query and presses send
   ```jsx
   handleSend() {
     chatAPI.execute({ workflow_id, query, session_id })
   }
   ```

2. **Backend API**: `/chat/execute` endpoint
   ```python
   # Get workflow from database
   workflow = db.query(Workflow).filter(id == workflow_id).first()
   
   # Create WorkflowExecutor
   executor = WorkflowExecutor({
     "id": workflow.id,
     "nodes": workflow.nodes,
     "edges": workflow.edges
   })
   
   # Execute
   result = await executor.execute(query)
   ```

3. **Workflow Executor**: Orchestrates execution
   ```python
   # Validate
   is_valid, msg = self.validator.validate()
   
   # Get execution order
   order = self.validator.get_execution_order()  # Topological sort
   
   # Execute each component
   for node_id in order:
     component = self.components[node_id]
     output = await component.execute(current_data)
     current_data = output  # Pass to next
   ```

4. **Components Execute in Order**:
   
   a. **UserQuery Component**:
   ```python
   # Normalize query format
   return {"query": query}
   ```
   
   b. **KnowledgeBase Component**:
   ```python
   # Generate embedding for query
   query_embedding = await self._generate_embedding(query)
   
   # Search ChromaDB
   results = chroma_client.query_embeddings(
     collection_name,
     query_embedding,
     n_results=5
   )
   
   # Return context
   return {"query": query, "context": combined_docs}
   ```
   
   c. **LLM Engine Component**:
   ```python
   # Build prompt
   prompt = self._build_prompt(query, context, web_context)
   
   # Call GPT
   response = openai_client.chat.completions.create(
     model="gpt-4o-mini",
     messages=[
       {"role": "system", "content": "You are helpful..."},
       {"role": "user", "content": prompt}
     ]
   )
   
   # Return response
   return {"response": response.choices[0].message.content}
   ```
   
   d. **Output Component**:
   ```python
   # Format final output
   return {"output": response_text}
   ```

5. **Save to Database**:
   ```python
   # Save user message
   user_msg = ChatMessage(role="user", content=query)
   db.add(user_msg)
   
   # Save assistant message
   assistant_msg = ChatMessage(role="assistant", content=output)
   db.add(assistant_msg)
   
   db.commit()
   ```

6. **Return to Frontend**:
   ```python
   return {
     "session_id": session.id,
     "user_message": user_msg,
     "assistant_message": assistant_msg
   }
   ```

7. **Frontend Updates UI**:
   ```jsx
   setMessages((msgs) => [
     ...msgs,
     { role: 'assistant', content: assistant_message.content }
   ]);
   ```

---

# Configuration & Setup

## Environment Variables

### Backend (`.env`)

```bash
# Database Connection
DATABASE_URL=postgresql://genai_user:genai_password@postgres:5432/genai_stack

# API Keys
OPENAI_API_KEY=sk-proj-xxxxx...
SERPAPI_API_KEY=xxxxx...

# Application Settings
APP_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:80

# Vector Store
CHROMA_PERSIST_DIR=/app/chroma_data

# Security
SECRET_KEY=your-secret-key-here
```

### Frontend (`.env`)

```bash
VITE_API_URL=http://localhost:8000
```

---

## Docker Configuration

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: genai_user
      POSTGRES_PASSWORD: genai_password
      POSTGRES_DB: genai_stack
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "genai_user"]
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://genai_user:genai_password@postgres:5432/genai_stack
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SERPAPI_API_KEY=${SERPAPI_API_KEY}
    volumes:
      - backend_uploads:/app/uploads
      - chroma_data:/app/chroma_data
    depends_on:
      postgres:
        condition: service_healthy
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  backend_uploads:
  chroma_data:
```

---

# Testing & Debugging

## Running Tests

### Backend Unit Tests

```bash
cd backend
pytest tests/

# Specific test file
pytest tests/test_components.py

# With coverage
pytest --cov=app tests/
```

### Test Structure

```python
# tests/test_components.py
import pytest
from app.components.user_query import UserQueryComponent

@pytest.mark.asyncio
async def test_user_query_component():
    component = UserQueryComponent("test-1", {"type": "userquery"})
    
    result = await component.execute("test query")
    
    assert result["query"] == "test query"
    assert result["component_type"] == "user_query"
```

## Debugging Tips

### Backend Debugging

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Use FastAPI Interactive Docs**:
   - Visit http://localhost:8000/docs
   - Test endpoints directly
   - View request/response schemas

3. **Database Inspection**:
   ```bash
   docker exec -it genai-postgres psql -U genai_user -d genai_stack
   \dt  # List tables
   SELECT * FROM workflows;
   ```

4. **ChromaDB Inspection**:
   ```python
   from app.vector_store.chromadb_client import chroma_client
   collections = chroma_client.client.list_collections()
   print(collections)
   ```

### Frontend Debugging

1. **React DevTools**: Install browser extension

2. **Console Logging**:
   ```jsx
   console.log('Nodes:', nodes);
   console.log('API Response:', response.data);
   ```

3. **React Query DevTools**:
   ```jsx
   import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
   
   <QueryClientProvider client={queryClient}>
     <App />
     <ReactQueryDevtools />
   </QueryClientProvider>
   ```

4. **Network Tab**: Monitor API calls in browser DevTools

---

# Summary

## Code Organization Principles

1. **Separation of Concerns**: API, Business Logic, Data Access are separate
2. **Dependency Injection**: FastAPI's dependency system for database sessions
3. **Factory Pattern**: Component creation via factory
4. **Template Method**: Base component with abstract execute method
5. **Strategy Pattern**: Different components implement same interface

## Key Design Patterns

- **Repository Pattern**: Database access through ORM
- **Service Layer**: Business logic in components and workflow engine
- **Controller**: FastAPI routers as controllers
- **Observer**: React Query for data synchronization

## Extensibility Points

1. **Add New Components**: Implement BaseComponent, register in factory
2. **Add New APIs**: Create new router file, include in main.py
3. **Add New Features**: Extend component configs, update UI
4. **Change LLM**: Replace OpenAI client in LLMEngineComponent

---

**End of Documentation**

For more details, see:
- Architecture Document: `/ARCHITECTURE.md`
- README: `/README.md`
- API Documentation: http://localhost:8000/docs
- GitHub: https://github.com/krayush7707/PlanetAiAssignment
