# 🤖 Multi-Agent System

A multi-agent AI system built with LangGraph orchestration, FastAPI backend, and Streamlit UI. Features real-time task monitoring, async processing, and Docker deployment.

## ✨ Key Features

- **🔄 Real-Time Monitoring**: WebSocket support for live task progress updates
- **🎨 Interactive UI**: Modular Streamlit dashboard
- **🚀 Async Processing**: Non-blocking task execution with background processing
- **🏗️ Deployment Ready**: Docker deployment with lifespan management
- **🤖 Multi-Agent Workflow**: Supervisor-orchestrated specialist agents
- **📡 REST API**: Comprehensive API with interactive documentation
- **🔧 Configurable**: YAML-based agent prompts and environment configuration
- **🏛️ Clean Architecture**: Modular design with separation of concerns

## 🏗️ Project Structure

```
multi-agent-system/
├── 🏗️ backend/                         # Backend service
│   ├── src/                            # Source code
│   │   ├── agents/                     # Agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py          # Abstract base class
│   │   │   ├── supervisor_agent.py    # Task orchestration
│   │   │   └── worker_agents.py       # Specialized workers
│   │   ├── api/                       # FastAPI endpoints
│   │   │   ├── __init__.py
│   │   │   └── endpoints.py           # REST API + WebSocket
│   │   ├── config/                    # Configuration
│   │   │   ├── __init__.py
│   │   │   └── agent_config.py        # LLM & agent setup
│   │   ├── models/                    # Data models
│   │   │   ├── __init__.py
│   │   │   ├── agent_state.py         # Core state model
│   │   │   ├── enums.py              # Agent roles & statuses
│   │   │   ├── requests.py           # API request models
│   │   │   └── responses.py          # API response models
│   │   ├── utils/                     # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── reporting.py          # Report generation
│   │   │   └── tools.py              # LangChain tools
│   │   ├── workflows/                 # LangGraph management
│   │   │   ├── __init__.py
│   │   │   └── workflow_manager.py   # Workflow orchestration
│   │   ├── system.py                  # Main controller
│   │   ├── api_server.py              # API server launcher
│   │   └── logger.py                  # Centralized logging
│   ├── prompts/                       # Agent prompts
│   │   └── agent_prompts.yaml
│   ├── requirements.txt               # Backend dependencies
│   └── Dockerfile                     # Backend container
├── 🎨 ui/                              # Frontend service (Refactored)
│   ├── src/                           # Source code
│   │   ├── app.py                     # Main Streamlit application (refactored)
│   │   ├── app_backup.py              # Original app backup
│   │   ├── ui_config.py               # Centralized UI configuration
│   │   ├── api_service.py             # Backend API communication (Repository pattern)
│   │   ├── websocket_manager.py       # Real-time updates (Observer pattern)
│   │   ├── components.py              # Reusable UI components (Factory pattern)
│   │   ├── page_handlers.py           # Page logic (Strategy pattern)
│   │   └── __init__.py                # Package initialization
│   ├── requirements.txt               # UI dependencies
│   └── Dockerfile                     # UI container
├── 📁 infrastructure/                  # Infrastructure and deployment configs
│   ├── 🐳 docker-compose.yml         # Production deployment
│   ├── 🔧 docker-compose.dev.yml     # Development overrides
│   ├── 📄 .env.example              # Environment variables template
│   └── README.md                     # Infrastructure documentation
├── 📦 pyproject.toml                  # Project configuration
├── 🚀 run.py                          # Main launcher script
├── run.sh / run.bat                   # Platform-specific scripts
└── requirements.txt                   # Aggregated dependencies
```

## � Learning Path & Code Structure

### 🎯 How to Learn This Codebase

Follow this sequential learning path to understand the system architecture and capabilities:

#### **Phase 1: Core Understanding (Start Here)**

1. **📋 Read This README** - Get overview of features and architecture
2. **🔧 Check Configuration** - `infrastructure/.env.example` - understand what APIs/keys are needed
3. **�🚀 Run the System** - Follow Quick Start to see it working
4. **🌐 Explore the UI** - Access http://localhost:8501 to understand user experience

#### **Phase 2: Data Models & Contracts**

5. **📊 Data Models** - `backend/src/models/` - understand the core data structures:
   - `agent_state.py` - Core state management model
   - `enums.py` - Agent roles, task statuses, and types
   - `requests.py` - API input models
   - `responses.py` - API output models

6. **⚙️ Configuration** - `backend/src/config/agent_config.py` - LLM and agent setup

#### **Phase 3: Agent System Architecture**

7. **🤖 Agent Foundation** - `backend/src/agents/`:
   - `base_agent.py` - Abstract base class (understand the agent interface)
   - `supervisor_agent.py` - Task orchestration and routing logic
   - `worker_agents.py` - Specialized agent implementations

8. **💬 Agent Prompts** - `backend/prompts/agent_prompts.yaml` - see how agents are instructed

#### **Phase 4: Workflow & Orchestration**

9. **🔄 Workflow Management** - `backend/src/workflows/workflow_manager.py` - LangGraph orchestration
10. **🎛️ Main Controller** - `backend/src/system.py` - high-level system coordination

#### **Phase 5: API & Communication**

11. **🌐 API Endpoints** - `backend/src/api/endpoints.py` - REST API + WebSocket implementation
12. **🔌 API Server** - `backend/src/api_server.py` - server startup and configuration

#### **Phase 6: Frontend Architecture (Modular Design)**

13. **🎨 UI Configuration** - `ui/src/ui_config.py` - centralized UI settings
14. **🏭 UI Components** - `ui/src/components.py` - reusable UI elements (Factory pattern)
15. **📡 API Service** - `ui/src/api_service.py` - backend communication (Repository pattern)
16. **🔄 WebSocket Manager** - `ui/src/websocket_manager.py` - real-time updates (Observer pattern)
17. **📄 Page Handlers** - `ui/src/page_handlers.py` - page logic (Strategy pattern)
18. **🖥️ Main UI App** - `ui/src/app.py` - main application entry point

#### **Phase 7: Utilities & Tools**

19. **🛠️ Utilities** - `backend/src/utils/`:
    - `tools.py` - LangChain tool integrations
    - `reporting.py` - report generation utilities

20. **📝 Logging** - `backend/src/logger.py` - centralized logging setup

#### **Phase 8: Deployment & Operations**

21. **🐳 Docker Setup** - `infrastructure/docker-compose.yml` - containerization
22. **🚀 Launch Scripts** - `run.py`, `run.sh`, `run.bat` - startup automation

### 🎓 Understanding Key Concepts

#### **Design Patterns Used**

##### **🎨 Frontend Patterns (UI Layer)**

- **Strategy Pattern**: `ui/src/page_handlers.py`
  - **What**: Defines a family of algorithms (page rendering strategies) and makes them interchangeable
  - **Where**: Different page handlers (SubmitTaskPageHandler, MonitorTasksPageHandler, SystemInfoPageHandler)
  - **Why**: Allows easy addition of new pages without modifying existing code, clean separation of page logic

- **Factory Pattern**: `ui/src/components.py`
  - **What**: Creates objects without specifying their exact classes, centralizes object creation logic
  - **Where**: ComponentFactory creates various UI elements (charts, forms, metrics)
  - **Why**: Consistent UI component creation, reusability, and centralized styling

- **Repository Pattern**: `ui/src/api_service.py`
  - **What**: Encapsulates data access logic and provides a uniform interface for data operations
  - **Where**: APIService handles all backend communication
  - **Why**: Abstracts API calls, centralizes error handling, makes testing easier

- **Observer Pattern**: `ui/src/websocket_manager.py`
  - **What**: Defines one-to-many dependency between objects for automatic notifications
  - **Where**: WebSocket manager notifies UI components of real-time updates
  - **Why**: Enables real-time UI updates without tight coupling between components

- **Singleton Pattern**: Service instances across UI modules
  - **What**: Ensures a class has only one instance and provides global access
  - **Where**: `api_service`, `websocket_manager`, `component_factory` instances
  - **Why**: Shared state management, resource efficiency, consistent configuration

##### **🏗️ Backend Patterns**

- **Template Method Pattern**: `backend/src/agents/base_agent.py`
  - **What**: Defines skeleton of algorithm in base class, lets subclasses override specific steps
  - **Where**: BaseAgent defines common agent workflow, specific agents implement specialized logic
  - **Why**: Code reuse, consistent agent interface, extensibility

- **Command Pattern**: `backend/src/models/requests.py`
  - **What**: Encapsulates requests as objects with all information needed to perform action
  - **Where**: TaskRequest encapsulates task execution commands
  - **Why**: Decouples request sender from receiver, enables queuing and logging

- **State Pattern**: `backend/src/models/agent_state.py`
  - **What**: Allows object to alter behavior when internal state changes
  - **Where**: AgentState manages task progression through different states
  - **Why**: Clean state transitions, maintainable workflow logic

- **Dependency Injection**: Throughout backend configuration
  - **What**: Provides dependencies to objects rather than having them create dependencies
  - **Where**: Agent configuration, LLM clients, tool integrations
  - **Why**: Testability, flexibility, loose coupling

##### **🤖 Agentic Patterns**

- **Supervisor-Worker Pattern**: `backend/src/agents/supervisor_agent.py`
  - **What**: One coordinator agent manages and delegates tasks to specialized worker agents
  - **Where**: SupervisorAgent orchestrates researcher, analyst, writer, and reviewer agents
  - **Why**: Task decomposition, specialization, parallel processing, fault isolation

- **Chain of Responsibility**: `backend/src/workflows/workflow_manager.py`
  - **What**: Passes requests through chain of handlers until one handles it
  - **Where**: Task flows through different agents in sequence
  - **Why**: Flexible workflow routing, easy to add/remove processing steps

- **Pipeline Pattern**: Agent workflow execution
  - **What**: Processes data through sequence of processing stages
  - **Where**: Task → Research → Analysis → Writing → Review → Results
  - **Why**: Modular processing, data transformation, quality assurance

#### **Architecture Principles**

- **Separation of Concerns**: Clear boundaries between UI, API, and business logic
- **Async Processing**: Non-blocking task execution
- **Event-Driven**: WebSocket-based real-time updates
- **Configuration-Driven**: Environment-based settings
- **Modular Design**: Interchangeable components

#### **Key Workflows to Understand**

1. **Task Submission Flow**: `UI → API → Agent System → Workflow Manager → Agents`
2. **Real-time Updates**: `Agents → WebSocket → UI Updates`
3. **Agent Coordination**: `Supervisor → Worker Agents → Results Aggregation`

### 🔍 Code Quality Features

- **Type Safety**: Pydantic models throughout
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured logging with different levels
- **Validation**: Input validation and configuration checks
- **Testing Ready**: Clean architecture enables easy testing

### 🚀 Development Workflow

1. **Start with Models** - Understand data structures
2. **Follow the Flow** - Trace a request from UI to backend
3. **Experiment** - Modify prompts or add new agent types
4. **Extend** - Add new API endpoints or UI components
5. **Deploy** - Use Docker for production deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Docker and Docker Compose (optional)
- API keys for Groq and Tavily

### 🔧 Environment Setup

```bash
# Clone and enter directory
git clone <your-repo>
cd multi-agent-system

# Set up environment variables
cp infrastructure/.env.example .env
# Edit .env with your API keys:
# GROQ_API_KEY=your_groq_api_key_here
# TAVILY_API_KEY=your_tavily_api_key_here

# Validate configuration
python validate_config.py
```

### 🐍 Local Development

#### Using uv (Recommended)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Install dependencies
uv sync

# Run both backend and UI
uv run python run.py both
```

#### Using pip
```bash
# Install dependencies
pip install -r requirements.txt

# Run backend and UI
python run.py both
```

#### Using convenience scripts
```bash
# Linux/Mac
./run.sh both

# Windows
run.bat both
```

### 🐳 Docker Deployment

#### Development with hot reload
```bash
docker compose -f infrastructure/docker-compose.yml -f infrastructure/docker-compose.dev.yml up
```

#### Production deployment
```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

#### Backend only
```bash
docker compose -f infrastructure/docker-compose.yml up backend
```

## 🌐 Access Points

Once running, you can access:

- **🎨 Streamlit UI**: http://localhost:8501
- **🔌 Backend API**: http://localhost:8000  
- **📚 API Documentation**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/health
- **🔄 WebSocket**: ws://localhost:8000/ws/tasks/{task_id}

## 🎯 Usage Examples

### 📱 Using the Streamlit UI

1. **Submit Task**: 
   - Navigate to http://localhost:8501
   - Enter your task description
   - Select task type and priority
   - Click "Submit Task"

2. **Monitor Progress**:
   - Switch to "Monitor Tasks" page
   - View real-time progress charts
   - See agent status and results
   - WebSocket updates automatically

3. **View Results**:
   - Completed tasks show full results
   - Download reports and findings
   - Review agent outputs

### 🔌 Using the API

#### Submit a task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Research the latest trends in AI and machine learning",
    "task_type": "research",
    "priority": 1
  }'
```

#### Monitor with WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tasks/TASK_ID');
ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('Task update:', update);
};
```

#### Check task status
```bash
curl -X GET "http://localhost:8000/tasks/{task_id}"
```

#### Stream progress
```bash
curl -N "http://localhost:8000/tasks/TASK_ID/stream"
```

## 🔧 Configuration

The system uses **pydantic-settings** for type-safe configuration management with automatic environment variable loading.

### Environment Variables

#### Required API Keys
```bash
GROQ_API_KEY=your_groq_api_key_here          # Required for LLM access
TAVILY_API_KEY=your_tavily_api_key_here      # Required for web search
```

#### Backend Configuration
```bash
# Server Configuration
HOST=0.0.0.0                                # Server host address
PORT=8000                                   # Server port
RELOAD=false                                # Enable auto-reload (dev mode)

# Agent Configuration  
MAX_ITERATIONS=10                           # Maximum workflow iterations
MODEL_NAME=llama-3.1-8b-instant           # LLM model name
TEMPERATURE=0.7                            # LLM temperature (0.0-2.0)
MAX_TOKENS=2000                            # Maximum tokens per response

# Logging
LOG_LEVEL=INFO                             # Logging level
```

#### UI Configuration
```bash
# Backend API Configuration
BACKEND_API_URL=http://localhost:8000      # Backend API base URL
BACKEND_WS_URL=ws://localhost:8000         # WebSocket base URL

# UI Behavior
APP_TITLE=Multi-Agent System               # Application title
LAYOUT=wide                                # Streamlit layout (wide/centered)
THEME=light                                # UI theme (light/dark)
ENABLE_WEBSOCKETS=true                     # Enable real-time updates
```

### Configuration Validation

Validate your configuration before running:
```bash
python validate_config.py
```

### Advanced Configuration

See `infrastructure/.env.example` for all available configuration options including:
- CORS settings
- WebSocket configuration  
- Task timeouts and limits
- Database settings (for future use)
- Feature flags

## 🏛️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI       │    │  Multi-Agent    │
│   (Modular)     │◄──►│   Backend       │◄──►│   System        │
│                 │    │                 │    │                 │
│ ├─ Components   │    │ ├─ REST API     │    │ ├─ Supervisor   │
│ ├─ Page Logic   │    │ ├─ WebSockets   │    │ ├─ Researcher   │
│ ├─ API Service  │    │ ├─ Lifespan     │    │ ├─ Analyst      │
│ └─ Config       │    │ └─ CORS         │    │ ├─ Writer       │
└─────────────────┘    └─────────────────┘    │ └─ Reviewer     │
                                              └─────────────────┘
```

### Agent Workflow
1. **Supervisor Agent**: Orchestrates task routing and coordination
2. **Researcher Agent**: Gathers information using web search tools
3. **Analyst Agent**: Analyzes data and identifies patterns
4. **Writer Agent**: Creates structured written content
5. **Reviewer Agent**: Performs quality assurance and validation

### Key Components
- **Agent System**: Individual agent implementations with base class
- **Workflow Management**: LangGraph orchestration and routing
- **State Management**: Pydantic models for type safety
- **Configuration**: Centralized configuration management
- **API Layer**: FastAPI endpoints with lifespan management
- **UI Layer**: Modular Streamlit components with design patterns
- **Utilities**: Supporting functions for tools and reporting
- **Real-time Communication**: WebSocket-based live updates

## 🛠️ Development

### 📁 Adding New Agents

1. Create agent class in `backend/src/agents/`
2. Extend `BaseAgent` class
3. Register in `WorkflowManager`
4. Add prompts to `agent_prompts.yaml`

### 🔧 Modifying API

1. Update endpoints in `backend/src/api/endpoints.py`
2. Add models in `backend/src/models/`
3. Test with integrated docs at `/docs`

### 🎨 UI Customization (Modular Architecture)

1. **Configuration**: Modify `ui/src/ui_config.py` for global settings
2. **Components**: Add new UI elements in `ui/src/components.py` (Factory pattern)
3. **Pages**: Create new page handlers in `ui/src/page_handlers.py` (Strategy pattern)
4. **API Integration**: Extend `ui/src/api_service.py` for new backend endpoints
5. **Real-time Features**: Enhance `ui/src/websocket_manager.py` for live updates
6. **Main App**: Update `ui/src/app.py` to register new pages/features

#### Example: Adding a New Page
```python
# In page_handlers.py
class NewPageHandler(PageHandler):
    def render(self):
        st.header("My New Page")
        # Your page logic here

# In app.py - update sidebar options
pages = ["Submit Task", "Monitor Tasks", "My New Page", "System Info"]
```

### 🧪 Testing

```bash
# Run tests (when implemented)
uv run pytest

# Type checking
uv run mypy backend/src/

# Code formatting
uv run black backend/src/ ui/src/
uv run isort backend/src/ ui/src/
```

### Package Management with uv
```bash
# Add a dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv sync

# Run scripts
uv run python script.py
```

## 🔍 Monitoring & Debugging

### 📊 Health Monitoring
- API health: `GET /health`
- System metrics: Built-in monitoring
- Task status: Real-time tracking
- Docker health checks configured

### 🐛 Debugging
```bash
# Enable debug mode
export LOG_LEVEL=DEBUG

# View logs
docker compose -f infrastructure/docker-compose.yml logs -f backend
docker compose -f infrastructure/docker-compose.yml logs -f ui
```

### Debug Commands
```bash
# Check container status
docker compose -f infrastructure/docker-compose.yml ps

# Test API connectivity
curl http://localhost:8000/health

# Test WebSocket
wscat -c ws://localhost:8000/ws/tasks/test
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure `GROQ_API_KEY` and `TAVILY_API_KEY` are set in `.env`
2. **API Connection Failed**: Check if backend is running on port 8000
3. **UI Not Loading**: Ensure Streamlit is running on port 8501
4. **WebSocket Errors**: Check browser WebSocket support and network connectivity
5. **Task Processing Stuck**: Check agent configuration and LLM API connectivity
6. **Import Errors**: Verify Python path includes the backend directory
7. **Docker Issues**: Check port availability and Docker daemon status

## 🐳 Deployment

### Build and Deploy
```bash
# Build and start services
docker compose -f infrastructure/docker-compose.yml up -d

# Scale services
docker compose -f infrastructure/docker-compose.yml up -d --scale backend=3
```
