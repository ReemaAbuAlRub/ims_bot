# Almamlaka TV Digital Expansion Initiative — Chatbot

A RAG chatbot that answers questions strictly from the three project PDFs in `artifacts/`, with
source citations, conflict flagging, bilingual (Arabic/English) multi-turn conversation, and
prompt-injection resistance.

## Architecture

- **`backend/`** — FastAPI service (OOP, PEP8). Ingests the PDFs into a local FAISS index
  (`intfloat/multilingual-e5-base` embeddings) and exposes the chat API. All RAG logic
  (loading, chunking, retrieval, prompting, the Claude call) and all persistence live here.
- **`frontend/`** — Streamlit app. A thin client: renders the chat UI and calls the backend
  over HTTP. Contains no RAG logic and stores no chat data.

The two run as separate processes and can be deployed independently.

### Data storage

Chat threads and messages are persisted by the backend in a SQL database via SQLAlchemy
(`backend/db/`): a `threads` table and a `messages` table, with messages cascade-deleted
alongside their thread. Each thread belongs to a `session_id` that the frontend keeps in the
page URL (`?sid=...`), so a visitor's chats come back after a refresh without needing a login.

- **Local development**: falls back to SQLite at `backend/data/chat.db` when `DATABASE_URL`
  is unset — no setup required.
- **Deployment**: set `DATABASE_URL` to a hosted Postgres. Streamlit Community Cloud has an
  ephemeral filesystem, so SQLite is *not* viable there.

### API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/threads?session_id=` | List a session's threads |
| `POST` | `/threads` | Create a thread |
| `GET` | `/threads/{id}` | Thread with its messages |
| `DELETE` | `/threads/{id}` | Delete a thread and its messages |
| `POST` | `/chat` | Answer a question in a thread, persisting both turns |
| `GET` | `/health` | Liveness check |

## Local setup

1. Create and activate a virtual environment, then install both requirement sets:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt -r frontend/requirements.txt
   ```
2. Copy `.env.example` to `.env` and set your key:
   ```bash
   cp .env.example .env
   # edit .env and set ANTHROPIC_API_KEY=sk-ant-...
   ```
3. (Optional) Pre-build the vector index — otherwise it's built automatically on backend startup:
   ```bash
   python -m backend.scripts.ingest
   ```
4. Run the backend (from the project root):
   ```bash
   uvicorn backend.main:app
   ```
   Avoid `--reload` here unless you scope it (`--reload-dir backend`) — by default it watches the
   entire project root, including `.venv/`, which causes a restart loop that never finishes
   startup.
5. In a second terminal, run the frontend:
   ```bash
   streamlit run frontend/app.py
   ```
   The frontend reads `BACKEND_URL` from the environment (defaults to `http://localhost:8000`).

## Deployment

1. **Database (Neon)**: create a free project at [neon.tech](https://neon.tech), copy its
   connection string, and convert the driver prefix to `postgresql+psycopg://`, keeping
   `?sslmode=require`. Tables are created automatically on backend startup — no migration
   step to run.
2. **Backend**: deploy to any Python host that runs a long-lived process (e.g. Render, Railway,
   Fly.io). Set `ANTHROPIC_API_KEY` and `DATABASE_URL` as secrets there. The FAISS index is
   built automatically on first startup.
3. **Frontend**: deploy to Streamlit Community Cloud pointed at `frontend/app.py`, with
   `BACKEND_URL` set (as an app secret) to the deployed backend's public URL.

The frontend needs no database credentials — only the backend talks to Postgres.

## Notes

- Branding uses the logo in `frontend/assets/`; `logo_white.png` (header knockout) and
  `logo_icon.png` (favicon) are generated from `logo.jpg`. `PRIMARY_COLOR` in
  `frontend/ui/theme.py` is sampled from the logo itself.
- Chats are keyed to the `?sid=` value in the URL, not to a user account: anyone with that URL
  sees those chats, and opening the app in a fresh tab starts a new empty session. Swap in real
  auth if that matters.
- The knowledge base is the fixed set of 3 PDFs in `artifacts/`; to change it, replace the PDFs
  and re-run `python -m backend.scripts.ingest` (or delete `backend/index/` and restart the
  backend).
