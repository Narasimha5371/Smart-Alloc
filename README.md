# Smart Alloc

Smart Alloc is a FastAPI-based web application for optimizing resource allocation across projects and teams. It provides a web UI for managers, HR, employees and clients to create and track projects, propose allocations, and use AI-assisted scoring for recommendations.

## Key Features

- Role-based UI (admin, HR, manager, employee, client)
- Project creation, submission, and review flows
- Allocation recommendation engine with AI confidence scores
- Notification system for allocation updates
- Server-side rendered templates using Jinja2 for a simple UI

## Prerequisites

- Python 3.10+ (the project was developed on Python 3.13)
- Git
- Recommended: a virtual environment tool (venv, virtualenv, or conda)

## Local development — quick start (Windows)

1. Clone the repo:

```powershell
git clone https://your.git.repo/smart-alloc.git
cd smart-alloc
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Copy the example environment file and edit as needed:

```powershell
copy .env.example .env
# Edit .env to set SECRET_KEY, DATABASE_URL, and other values
```

5. Initialize the database (Alembic migrations are included):

```powershell
# stamp the DB at the migrations head (no schema changes applied)
python -m alembic stamp head
# or if you want to run migrations:
python -m alembic upgrade head
```

6. Seed sample data (optional):

```powershell
python -m app.seed
```

7. Start the dev server:

```powershell
$env:DEBUG = "True"
uvicorn app.main:app --reload --port 8000
# If uvicorn is not installed, install it in the venv:
python -m pip install "uvicorn[standard]"
```

Open http://127.0.0.1:8000 in your browser.

## Running Tests

Run the provided smoke test to verify basic site functionality:

```powershell
python -m pytest tests/smoke_test.py
```

You can also run `tests/check_hr.py` and `tests/check_hr_verbose.py` for focused HR dashboard checks.

## Common Commands

- Install requirements: `python -m pip install -r requirements.txt`
- Run migrations: `python -m alembic upgrade head`
- Stamp DB to head (no schema changes applied): `python -m alembic stamp head`
- Seed DB: `python -m app.seed`
- Run dev server: `uvicorn app.main:app --reload --port 8000`

## Troubleshooting

- `uvicorn` not found: ensure your virtualenv is activated and `uvicorn` is installed in it.
- 500 errors during page render: check server logs (they are printed to the console). Many 500s in this app stem from template rendering errors — ensure templates reference existing model attributes.
- Alembic commands failing under interactive shells: run them from a normal PowerShell/CMD prompt (not inside a Python REPL).

If you see a Jinja2 `UndefinedError` mentioning a missing attribute (for example `ai_confidence`), inspect the template in `app/templates/` and confirm the model field in `app/models/` (e.g., `ai_confidence_score`).

## Deployment Notes

- For production use, set `DEBUG=False` and use a production ASGI server (Uvicorn/Gunicorn with workers) behind a reverse proxy.
- Securely set `SECRET_KEY` and production `DATABASE_URL` via environment variables or a secrets store.
- Add HTTPS/TLS and configure session/cookie security flags.

## Development Tips

- Keep model attributes and templates in sync to avoid runtime template errors.
- Use `tests/smoke_test.py` after making changes to quickly validate the main user flows.
- Consider adding CI to run `pytest` and linting checks on every PR.

## Contributing

Please open issues or PRs. For code changes:

1. Fork the repository
2. Create a feature branch
3. Run tests locally
4. Open a PR with a clear description and the related issue

## License

This project is licensed under the MIT License.

## Where to find things

- App code: `app/`
- Templates: `app/templates/`
- Routers: `app/routers/`
- DB models: `app/models/`
- Tests: `tests/`
- Alembic migrations: `alembic/`

If you want a quick pointer, see the HR dashboard template at `app/templates/hr/dashboard.html` and the corresponding model at `app/models/project.py`.