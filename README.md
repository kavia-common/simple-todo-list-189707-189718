# simple-todo-list-189707-189718

Simple Todo List application with:
- backend_api: FastAPI + SQLite for CRUD
- frontend_app: React UI (calls backend via REST)

## Backend (backend_api)

Run locally (uvicorn):
- Ensure dependencies: see backend_api/requirements.txt
- Start: uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001

OpenAPI docs: /docs

### Endpoints
- GET /tasks: list all tasks
- POST /tasks: create a task {title, description?}
- PUT /tasks/{id}: update any of {title?, description?, completed?}
- DELETE /tasks/{id}: delete a task

### Database
- SQLite file located under backend_api/data/todo.db by default.
- You can change filename via env var SQLITE_DB_FILENAME.

### CORS
CORS is enabled for all origins for preview. Restrict in production as needed.

## Frontend (frontend_app)
The React app (port 3000) calls the backend at port 3001:
- Backend base URL: http://localhost:3001

Ensure both containers are running for full functionality.