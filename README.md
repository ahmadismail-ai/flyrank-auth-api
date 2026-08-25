# FlyRank Auth API

A FastAPI authentication API using Supabase Auth.

## Requirements

- Python 3.11+
- Supabase project
- Virtual environment recommended

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install application dependencies:

python -m pip install -r requirements.txt

Install development/test dependencies:

python -m pip install -r requirements-dev.txt
Environment Variables

Create a .env file based on .env.example:

SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
PORT=8000

Do not commit .env or real Supabase credentials.

Run the API
uvicorn app.main:app --port 8000

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs
Endpoints
MethodEndpointDescription
GET/API health/root response
POST/auth/signupCreate a user
POST/auth/loginAuthenticate a user
GET/auth/meGet the authenticated user
POST/auth/logoutLog out the authenticated user

Protected endpoints require:

Authorization: Bearer <access_token>
Run Tests

Run the complete test suite:

python -m pytest -q

The test suite uses mocked Supabase authentication, so the tests do not require live Supabase requests.

Project Structure
flyrank-auth-api/
+-- app/
¦   +-- __init__.py
¦   +-- auth.py
¦   +-- main.py
¦   +-- models.py
+-- tests/
¦   +-- __init__.py
¦   +-- test_auth.py
¦   +-- test_api.py
+-- .env.example
+-- .gitignore
+-- requirements.txt
+-- requirements-dev.txt
+-- README.md
