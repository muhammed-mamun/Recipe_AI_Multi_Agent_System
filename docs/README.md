# recipe AI Multi-Agent System

## Prerequisites

- Node.js (v18+)
- Python (v3.10+)
- Supabase CLI (optional, for local backend)

## Running the Project

### Backend

1.  Navigate to the root directory.
2.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
3.  Install dependencies (if not already installed):
    ```bash
    pip install -r backend/requirements.txt
    ```
4.  Start the backend server:
    ```bash
    uvicorn backend.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

### Frontend

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies (if not already installed):
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:3000`.
