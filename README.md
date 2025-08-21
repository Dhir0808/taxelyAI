# Taxely Monorepo

A demo multi-agent tax copilot using Portia SDK + FastAPI backend and Next.js frontend.

## Structure

- `apps/web` — Next.js (App Router) UI
- `services/portia` — Python FastAPI service using Portia SDK and offline tools

## Backend (FastAPI + Portia SDK)

```bash
cd services/portia
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
cp .env.example .env
uvicorn src.portia_app:app --reload --port 8000
```

## Frontend (Next.js)

```bash
cd apps/web
npm i
NEXT_PUBLIC_AGENT_URL=http://localhost:8000/api/run npm run dev
```

Open `http://localhost:3000`, click "Run Taxely".

### Test data

- Company Number: `01234567`
- Revenue: `20000000`
- Expenses: `14000000`
- R&D: `3000000`
- Patent: `5000000`
- CapEx: `1000000`

### Notes

- Free Companies House API is used; if it fails, a mock is returned and marked `fallback: true`.
- Guardrails: "Hackathon demo. Not tax advice." "Marginal relief approximated linearly." "Patent Box/AIA modeled illustratively."
