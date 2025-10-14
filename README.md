# Multivendor Adapter Module

This project provides a Flask backend and React frontend for a multivendor adapter enabling:
- Upload of NB (northbound JSON) and SB (southbound YANG/MIB/CLI) models (API 1)
- Configuration of mappings between NB and SB models (API 2)
- Triggering provisioning with basic transformation pipeline and stubbed southbound handlers for NETCONF and SNMP/CLI (API 3)
- Authentication with RBAC (session tokens stored in DB)
- PostgreSQL database with Alembic migrations and seed data (default admin)

Structure:
- backend/ (Flask app, SQLAlchemy, Alembic)
- frontend/ (React app)
- openapi.yaml (backend API summary)
- .env.example (root) and frontend/.env.example

Environment variables:
See .env.example (root) and frontend/.env.example.

Database
- Uses PostgreSQL accessible at localhost on port 5001 (preview database port)
- Connection string sample: postgresql://USER:PASSWORD@localhost:5001/DBNAME

Quick start (development)
1) Backend
- Create Python venv and install dependencies:
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r backend/requirements.txt

- Copy .env.example to .env and fill values (no real secrets in repo):
  cp .env.example .env

- Initialize DB and run migrations:
  cd backend
  alembic upgrade head
  cd ..

- Run backend:
  export FLASK_APP=backend/wsgi.py
  flask run --host 0.0.0.0 --port 5000

2) Frontend
- Install deps:
  cd frontend
  npm install
  cp .env.example .env
  # set REACT_APP_API_BASE_URL to backend URL, e.g. http://localhost:5000
  npm start

API overview
Auth:
- POST /api/auth/login
- POST /api/auth/logout

Models:
- POST /api/models  (payload: {type: "NB"|"SB", name, data, version?})
- GET /api/models

Mappings:
- POST /api/mappings  (payload: {nb_model_id, sb_model_id, mapping_data})
- GET /api/mappings

Provision:
- POST /api/provision  (payload: {mapping_id, nb_model_id? or nb_inline?})
  - Applies mapping to transform NB to SB
  - Stubs southbound via NETCONF or SNMP/CLI based on sb model type or request

Admin lists:
- GET /api/admin/users
- GET /api/admin/roles
- GET /api/admin/sessions
- GET /api/admin/audit_logs
- GET /api/admin/versions

RBAC
- Basic role-permission model; protected routes require 'admin' or relevant permissions.

Error schema
- { "code": "string", "message": "string", "details": { ... } }

OpenAPI
- See openapi.yaml

Notes
- This initial scaffold is meant for development and demonstration, with stub southbound clients.
- Ensure DB is reachable at localhost:5001 (or set DATABASE_URL accordingly).
