Movie Rating System (FastAPI)

A backend API for managing movies and submitting ratings, built with FastAPI + SQLAlchemy + PostgreSQL.
This project is implemented in phases (Back-End, Logging, Docker, Seed DB) based on the provided project docs.

---

1. Features

---

* Movies CRUD (create, read, update, delete)
* Filtering + pagination for movie list
* Ratings submission (1..10) for movies
* Structured API responses (success/failure)
* Centralized logging (Phase 2)
* Seed database from TMDB dataset (Phase Seed)

---

2. Tech Stack

---

* Python (>= 3.13)
* FastAPI
* SQLAlchemy (ORM)
* PostgreSQL (psycopg2)
* Poetry (dependency management)

---

3. Project Structure

---

Root
app/
main.py                  FastAPI app entrypoint
controllers/             API routes (endpoints)
services/                Business logic
repositories/            DB operations
models/                  SQLAlchemy models
schemas/                 Pydantic schemas (DTOs)
db/
session.py             Engine + SessionLocal + Base + get_db
init_db.py             Create tables (Base.metadata.create_all)
core/
logging_config.py      Logging setup (Phase 2)

scripts/
seeddb.sql               Seed script (psql)
seed_check.py            Simple sanity check script
tmdb_5000_movies.csv
tmdb_5000_credits.csv

---

4. Requirements

---

* Python 3.13+
* PostgreSQL running locally (or accessible via network)
* Poetry installed

---

5. Configuration

---

The application reads database settings from environment variables.

Environment Variables

* DATABASE_URL (required)
  Example:
  postgresql+psycopg2://movieuser:moviepass@localhost:5432/moviedb

Recommended: create a .env file in the project root and set DATABASE_URL there.

Example .env content (one line):
DATABASE_URL=postgresql+psycopg2://movieuser:moviepass@localhost:5432/moviedb

---

6. Setup (Local)

---

Step 1) Install dependencies
Command:
poetry install

Step 2) Create database tables
This project includes a simple initializer that creates tables directly from SQLAlchemy models.

Command:
poetry run python -m app.db.init_db

Step 3) Run the API
Command:
poetry run uvicorn app.main:app --reload

After running, open:

* Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

7. API Overview

---

Base prefix:

* /api/v1/movies

Common endpoints (high-level):

* GET    /api/v1/movies                      List + filters + pagination
* GET    /api/v1/movies/{movie_id}           Movie details
* POST   /api/v1/movies                      Create a movie
* PUT    /api/v1/movies/{movie_id}           Update a movie
* DELETE /api/v1/movies/{movie_id}           Delete a movie
* POST   /api/v1/movies/{movie_id}/ratings   Submit a rating

Pagination & Filtering
List endpoint supports:

* page (default: 1)
* page_size (implementation) OR size_page (as written in docs/spec)
* optional filters: title, release_year, genre

---

8. Database Seeding (TMDB)

---

The seed script uses psql and \copy to load data from:

* scripts/tmdb_5000_movies.csv
* scripts/tmdb_5000_credits.csv

Important note about \copy:

* \copy reads CSV files from the client-side working directory (where you run psql).
* To avoid path issues, run seeding from inside the scripts/ directory.

Seed steps

1. Ensure tables exist:
   Command:
   poetry run python -m app.db.init_db

2. Run seed (run from scripts/ directory):
   Command sequence:
   cd scripts
   psql -U <username> -d <db_name> -h localhost -f seeddb.sql

3. Optional sanity check:
   Command sequence:
   cd ..
   poetry run python scripts/seed_check.py

---

9. Logging (Phase 2)

---

Logging is configured in:

* app/core/logging_config.py

The application initializes logging at startup and prints logs to stdout (console).
Key API calls such as listing movies and submitting ratings are logged as per Phase 2 requirements.

---

10. Development Workflow (Git)

---

Branching policy:

* Always work from develop
* For each task, create a dedicated branch from develop and open a PR back to develop

Example:
git checkout develop
git pull
git checkout -b feat/some-feature

---

11. Commit Message Convention

---

Commit message format: <type>: <short summary>
[optional body: why/how]
[optional footer: issue references, notes]

Allowed types:

* init     initial scaffolding
* feat     new feature
* fix      bug fix
* style    formatting changes without logic changes
* refactor code cleanup without new behavior
* docs     documentation changes
* chore    tooling/config/maintenance

Rules:

* Summary maximum 72 characters
* Use imperative mood (e.g., “add”, “update”, “fix”, “remove”, “implement”)
* One logical change per commit

Examples:
init: scaffold project structure
feat: add movie ratings endpoint
fix: validate release_year input
docs: update README with setup steps

---

12. Troubleshooting

---

Poetry error: README.md does not exist

* This project expects a README.md file referenced in pyproject.toml.
* Ensure README.md exists in the repository root.

DATABASE_URL is not set
If you see:
ValueError: DATABASE_URL is not set in the environment variables.
Then:

* Create a .env file in the project root
* Set DATABASE_URL with a valid PostgreSQL connection string

---

13. License (MIT)

---

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
