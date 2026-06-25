# Pitchly

Pitchly is a React/Vite frontend with a FastAPI backend.

## Local development

Prerequisites:

- Node.js 20+
- Python 3.11
- Supabase project credentials
- Gemini API key for analysis

Install dependencies:

```bash
npm run install:frontend
cd pitchly-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create environment files:

```bash
copy pitchly\.env.example pitchly\.env
copy pitchly-backend\.env.example pitchly-backend\.env
```

Update the copied `.env` files with real Supabase, database, and Gemini values.

Run locally in two terminals:

```bash
npm run dev:backend
npm run dev:frontend
```

The frontend runs at `http://localhost:5173` and the backend health check is `http://localhost:8000/health`.

## Production build

```bash
npm run build
```

The frontend build is emitted to `pitchly/dist`.

## Deployment

The repository includes `render.yaml` for deploying both services on Render:

- `pitchly-api`: FastAPI web service from `pitchly-backend`
- `pitchly-web`: static Vite site from `pitchly`

Required backend environment variables:

- `GEMINI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`
- `DATABASE_URL`
- `FRONTEND_URL`
- `CORS_ORIGINS`
- `ENVIRONMENT=production`

Required frontend environment variables:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_API_URL`

Set `VITE_API_URL` to the deployed backend URL and include the deployed frontend URL in backend `CORS_ORIGINS`.
