# Almamlaka TV Digital Expansion Initiative — Chatbot

A RAG chatbot that answers questions strictly from the three project PDFs in `artifacts/`, with
source citations, conflict flagging, bilingual (Arabic/English) multi-turn conversation, and
prompt-injection resistance.

## Architecture

- **`backend/`** — the whole service layer (OOP, PEP8): PDF loading, chunking, embedding,
  FAISS retrieval, prompt building, the Claude call, and persistence. Contains no Streamlit
  imports, and also runs standalone as a FastAPI app.
- **`frontend/`** — Streamlit app. Renders the chat UI only; contains no RAG logic and stores
  no chat data itself.

**Two ways to run the same code:**

| Mode | How the frontend reaches the backend | When |
|---|---|---|
| Single process | Imports the backend package directly (`frontend/local_client.py`) | Default, and how it deploys to Streamlit Cloud |
| Two services | HTTP calls to a running FastAPI server (`frontend/api_client.py`) | When `BACKEND_URL` is set |

Both clients expose the same methods, so `app.py` is identical either way. The split is
enforced in the code, not by the deployment topology.

### Data storage

Chat threads and messages are persisted by the backend in a SQL database via SQLAlchemy
(`backend/db/`): a `threads` table and a `messages` table, with messages cascade-deleted
alongside their thread. Each thread belongs to a `session_id` that the frontend keeps in the
page URL (`?sid=...`), so a visitor's chats come back after a refresh without needing a login.

- **Local development**: falls back to SQLite at `backend/data/chat.db` when `DATABASE_URL`
  is unset — no setup required.
- **Deployment**: set `DATABASE_URL` to a hosted Postgres. Streamlit Community Cloud has an
  ephemeral filesystem, so SQLite is *not* viable there.

### API (two-service mode only)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/threads?session_id=` | List a session's threads |
| `POST` | `/threads` | Create a thread |
| `GET` | `/threads/{id}` | Thread with its messages |
| `DELETE` | `/threads/{id}` | Delete a thread and its messages |
| `POST` | `/chat` | Answer a question in a thread, persisting both turns |
| `GET` | `/health` | Liveness check |

## Local setup

1. Create and activate a virtual environment, then install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set your key:
   ```bash
   cp .env.example .env
   # edit .env and set ANTHROPIC_API_KEY=sk-ant-...
   ```
3. Run the app:
   ```bash
   streamlit run frontend/app.py
   ```
   The vector index is built automatically on first run. Leave `BACKEND_URL` unset to run
   everything in one process.

### Running as two services (optional)

```bash
uvicorn backend.main:app                    # terminal 1
BACKEND_URL=http://localhost:8000 streamlit run frontend/app.py   # terminal 2
```

Avoid `uvicorn --reload` unless you scope it (`--reload-dir backend`) — by default it watches
the project root including `.venv/`, causing a restart loop that never finishes startup.

## Deployment (Streamlit Community Cloud)

1. **Database**: create a free project at [neon.tech](https://neon.tech), copy its connection
   string, and change the driver prefix to `postgresql+psycopg://`, keeping `?sslmode=require`.
   Tables are created automatically on first run — no migration step.
2. **App**: at [share.streamlit.io](https://share.streamlit.io), deploy this repo with main file
   `frontend/app.py`.
3. **Secrets** (Advanced settings → Secrets):
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   DATABASE_URL = "postgresql+psycopg://...?sslmode=require"
   ```
   Leave `BACKEND_URL` out — its absence is what selects single-process mode.

Notes on the free tier: apps get 690 MB–2.7 GB RAM, which fits this stack. The filesystem is
ephemeral, so the embedding model and FAISS index are rebuilt on each cold start (~1 min) and
SQLite would not persist — hence Postgres.

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
