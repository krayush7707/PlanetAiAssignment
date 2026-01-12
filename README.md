# GenAI Stack - No-Code Workflow Builder

A full-stack No-Code/Low-Code web application that enables users to visually create and interact with intelligent workflows using drag-and-drop components.

## 🚀 Features

- **Visual Workflow Builder** - Drag-and-drop interface built with React Flow
- **4 Core Components**:
  - **User Query** - Entry point for user input
  - **Knowledge Base** - PDF upload, text extraction, vector embeddings, RAG retrieval
  - **LLM Engine** - OpenAI GPT integration with custom prompts and web search
  - **Output** - Display final results
- **Chat Interface** - Test workflows with interactive chat
- **Workflow Persistence** - Save and load workflows from PostgreSQL
- **Chat History** - Persistent conversation history
- **Document Processing** - PDF text extraction with PyMuPDF and OpenAI embeddings
- **Vector Search** - ChromaDB for semantic search
- **Web Search** - SerpAPI integration for real-time information

## 🛠 Tech Stack

### Frontend
- **React** + **Vite** - Fast modern development
- **React Flow** - Visual workflow canvas
- **TailwindCSS** - Styling with custom design system
- **Zustand** - State management
- **React Query** - API data fetching
- **Axios** - HTTP client
- **Lucide Icons** - Icon library

### Backend
- **FastAPI** - High-performance Python API
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM
- **ChromaDB** - Vector store
- **OpenAI** - GPT-4 and text embeddings
- **SerpAPI** - Web search
- **PyMuPDF** - PDF text extraction

### Deployment
- **Docker** + **Docker Compose** - Containerization
- **Nginx** - Frontend serving and reverse proxy

## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API key
- SerpAPI key (for web search feature)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd PlanetAiAssignment
```

### 2. Configure Environment Variables

Create `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

Also create backend `.env`:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with the same API keys.

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

This will start:
- **Frontend** - http://localhost:80
- **Backend API** - http://localhost:8000
- **PostgreSQL** - localhost:5432
- **API Docs** - http://localhost:8000/docs

### 4. Access the Application

Open your browser and navigate to:
- **Application**: http://localhost:80
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### Creating Your First Workflow

1. **Create a New Stack**
   - Click "+ New Stack" button
   - Enter name (e.g., "Chat With PDF")
   - Enter description
   - Click "Create"

2. **Build Your Workflow**
   - Drag components from the left sidebar onto the canvas
   - Connect components by dragging from output handle to input handle
   - Example flow: `User Query → Knowledge Base → LLM Engine → Output`

3. **Configure Components**
   - Click on any component to open configuration panel
   - **Knowledge Base**: Upload PDF documents
   - **LLM Engine**: Select model (GPT-4o-Mini), set temperature, enable web search
   - Configure custom prompts with placeholders: `{query}`, `{context}`

4. **Save Workflow**
   - Click "Save" button in top right

5. **Test with Chat**
   - Click "Chat with Stack" button
   - Enter your query in the chat interface
   - View AI-generated responses

### Example Workflows

#### 1. Simple AI Chat
```
User Query → LLM Engine → Output
```

#### 2. Document Q&A (RAG)
```
User Query → Knowledge Base (with uploaded PDFs) → LLM Engine → Output
```

#### 3. Web-Enhanced Chat
```
User Query → LLM Engine (with web search enabled) → Output
```

## 🏗 Project Structure

```
PlanetAiAssignment/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── documents.py  # Document upload/management
│   │   │   ├── workflows.py  # Workflow CRUD
│   │   │   ├── chat.py       # Chat execution
│   │   │   └── health.py     # Health check
│   │   ├── components/       # Workflow components
│   │   │   ├── base.py
│   │   │   ├── user_query.py
│   │   │   ├── knowledgebase.py
│   │   │   ├── llm_engine.py
│   │   │   └── output.py
│   │   ├── database/         # Database models & schemas
│   │   ├── vector_store/     # ChromaDB client
│   │   └── workflow/         # Workflow validator & executor
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── store/           # State management
│   │   ├── App.jsx          # Main app component
│   │   └── index.css        # Global styles
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## 🔧 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env
# Edit .env with your API keys

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Copy and configure .env
cp .env.example .env

# Run development server
npm run dev
```

Visit http://localhost:5173

### Database Setup

The application automatically creates database tables on startup. To manually initialize:

```python
from app.database.connection import init_db
init_db()
```

## 🗄 Database Schema

### Tables

- **documents** - Uploaded file metadata and processing status
- **workflows** - Workflow definitions (nodes, edges, validation status)
- **chat_sessions** - Chat conversation sessions
- **chat_messages** - Individual messages in conversations

## 🔌 API Endpoints

### Workflows
- `GET /workflows/` - List all workflows
- `POST /workflows/` - Create workflow
- `GET /workflows/{id}` - Get workflow
- `PUT /workflows/{id}` - Update workflow
- `DELETE /workflows/{id}` - Delete workflow
- `POST /workflows/{id}/validate` - Validate workflow

### Documents
- `GET /documents/` - List documents
- `POST /documents/upload` - Upload PDF
- `DELETE /documents/{id}` - Delete document

### Chat
- `POST /chat/execute` - Execute workflow with query
- `GET /chat/sessions/{id}` - Get chat session with messages

### Health
- `GET /health/` - Check system health

Full API documentation available at http://localhost:8000/docs

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v

# Rebuild specific service
docker-compose build backend
docker-compose up backend
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Manual Testing

1. Test document upload in API docs: http://localhost:8000/docs
2. Create a workflow via UI
3. Upload a PDF document
4. Configure Knowledge Base component to use uploaded document
5. Test chat with questions about the document

## 🔍 Troubleshooting

### Database Connection Errors
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check database logs: `docker-compose logs postgres`

### API Key Errors
- Verify `.env` file exists and contains valid API keys
- Restart containers after updating `.env`: `docker-compose restart`

### Frontend Build Errors
- Clear node_modules: `rm -rf frontend/node_modules`
- Reinstall: `cd frontend && npm install`

### ChromaDB Errors
- Clear vector store: `docker-compose down -v`
- Restart: `docker-compose up`

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://genai_user:genai_password@localhost:5432/genai_stack
OPENAI_API_KEY=your_key_here
SERPAPI_API_KEY=your_key_here
CHROMA_PERSIST_DIR=./chroma_data
DEBUG=True
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🎨 Design Reference

The UI follows the Figma design with:
- **Primary Color**: #4CAF50 (Green)
- **Secondary Color**: #2196F3 (Blue)
- **Typography**: Inter font family
- **Component Cards**: Rounded corners with subtle shadows
- **Chat Interface**: User messages in light blue, AI responses in white

## 🚧 Future Enhancements

- [ ] User authentication and authorization
- [ ] Workflow templates library
- [ ] Real-time collaboration
- [ ] More component types (API calls, data transformations)
- [ ] Workflow scheduling and automation
- [ ] Analytics and monitoring dashboard
- [ ] Export/import workflows
- [ ] Version control for workflows

## 📄 License

This project is created as an assignment for Planet AI.

## 👥 Authors

Built with ❤️ for the Planet AI Full-Stack Engineer assignment

## 🙏 Acknowledgments

- OpenAI for GPT and embeddings API
- React Flow for the excellent workflow visualization library
- FastAPI for the modern Python web framework
- The open-source community

---

**Need Help?** Check the API documentation at http://localhost:8000/docs or review the implementation plan in the `/brain` artifacts directory.
