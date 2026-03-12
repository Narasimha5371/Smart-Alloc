# Smart-Alloc: AI-Powered Project Management Platform

Smart-Alloc is an intelligent project management web application that leverages AI to streamline project evaluation and employee allocation.

## Features

- **AI Project Evaluation**: Automatically analyze project viability based on company capabilities
- **Smart Employee Matching**: AI-powered skill-based employee recommendation for projects
- **Role-Based Access Control**: Five roles — Admin, HR, Manager, Employee, Client
- **Spreadsheet Import**: Bulk import employees via .xlsx or .csv files
- **Real-time Progress Tracking**: Employees update progress, managers monitor via dashboards
- **Notification System**: In-app notifications for assignments and project updates

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Jinja2 + Bootstrap 5.3
- **Database**: SQLite with SQLAlchemy 2.0 ORM
- **AI**: Groq API (LLaMA models)
- **Auth**: JWT (HttpOnly cookies)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and set your values:
```bash
cp .env.example .env
```

Key settings:
- `SECRET_KEY`: Change to a random secret for production
- `GROQ_API_KEY`: Your Groq API key (get one at https://console.groq.com)

### 3. Seed the Database

```bash
python -m app.seed
```

This creates sample users, skills, and projects for testing.

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000

## Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@smartalloc.com | admin123 |
| HR | hr@smartalloc.com | hr123456 |
| Manager | manager1@smartalloc.com | manager123 |
| Employee | alice@smartalloc.com | employee123 |
| Client | client1@example.com | client123 |

## Architecture

```
app/
├── main.py              # FastAPI application factory
├── config.py            # Environment configuration
├── database.py          # SQLAlchemy setup
├── dependencies.py      # Auth & RBAC dependencies
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic validation schemas
├── routers/             # API & page route handlers
├── services/            # Business logic layer
├── utils/               # Security, file parsing helpers
├── templates/           # Jinja2 HTML templates
└── static/              # CSS, JS, images
```

## Workflow

1. **Client** submits a project with requirements
2. **HR** triggers AI evaluation → AI recommends accept/reject
3. HR makes the final decision (accept or reject)
4. **Manager** views accepted projects, triggers AI employee suggestions
5. Manager allocates employees from AI recommendations
6. **Employees** get notified, update progress, manage skills
7. Progress is tracked across all dashboards

## Spreadsheet Import Format

CSV or XLSX with columns:
- `email` (required)
- `full_name` (required)
- `department` (optional)
- `password` (optional, defaults to "changeme123")
- `skills` (optional, comma-separated skill names)
