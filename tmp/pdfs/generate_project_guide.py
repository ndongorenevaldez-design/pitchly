from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = r"C:\Users\ndong\Desktop\pitchly\Pitchly_Project_Guide.pdf"


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            textColor=colors.HexColor("#172554"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#475569"),
            alignment=TA_CENTER,
            spaceAfter=24,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e3a8a"),
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155"),
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8,
            leading=11,
            backColor=colors.HexColor("#f1f5f9"),
            borderColor=colors.HexColor("#cbd5e1"),
            borderWidth=0.5,
            borderPadding=5,
            spaceAfter=7,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            leftIndent=10,
            textColor=colors.HexColor("#1f2937"),
        ),
    }


S = styles()


def p(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    flowables = []
    for item in items:
        flowables.append(p(f"- {item}", "bullet"))
    flowables.append(Spacer(1, 4))
    return flowables


def code(text):
    return Preformatted(text, S["code"])


def table(rows, widths):
    data = [[p(str(cell), "small") for cell in row] for row in rows]
    t = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#dbeafe"))
    canvas.setLineWidth(0.7)
    canvas.line(0.65 * inch, 10.35 * inch, 7.85 * inch, 10.35 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(0.65 * inch, 10.47 * inch, "Pitchly Project Guide")
    canvas.drawRightString(7.85 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.65 * inch,
        title="Pitchly Project Guide",
        author="Codex",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="guide", frames=[frame], onPage=header_footer)])

    story = [
        Spacer(1, 1.4 * inch),
        p("Pitchly Project Guide", "title"),
        p(
            "Codebase explanation, language overview, runtime flow, navigation map, and deployment notes.",
            "subtitle",
        ),
        p(
            "Project root: C:\\Users\\ndong\\Desktop\\pitchly. This document describes the current repository after adding local run commands and deployment support.",
            "body",
        ),
        Spacer(1, 0.3 * inch),
        table(
            [
                ["Area", "Technology", "Purpose"],
                ["Frontend", "React, TypeScript, Vite", "Browser app, routing, authentication screens, recording flow, dashboards, and results UI."],
                ["Backend", "Python, FastAPI, Uvicorn, Gunicorn", "API service, authentication verification, uploads, session orchestration, results, and health checks."],
                ["Storage/Auth", "Supabase", "User authentication, token validation, database connection, and private video storage."],
                ["Analysis", "Gemini API placeholder plus Python pipeline", "Session analysis workflow currently produces demo results through a background job."],
                ["Deployment", "Render, Vercel/Netlify helpers", "Production build and hosting configuration for frontend and backend."],
            ],
            [1.2 * inch, 1.7 * inch, 4.1 * inch],
        ),
        PageBreak(),
    ]

    story += [
        p("1. High-Level Architecture", "h1"),
        p(
            "Pitchly is split into two applications under one repository. The `pitchly` folder is the client-side React application. The `pitchly-backend` folder is the FastAPI backend. The root folder now provides shared convenience scripts, documentation, and deployment configuration.",
        ),
        bullets(
            [
                "The browser loads the Vite React app and uses React Router for page navigation.",
                "Supabase handles login, signup, password reset, email verification, and browser-side auth sessions.",
                "The frontend attaches the Supabase bearer token to backend API requests through an Axios interceptor.",
                "The backend verifies bearer tokens with Supabase admin credentials before allowing protected requests.",
                "Recorded videos are uploaded to Supabase Storage through backend upload endpoints.",
                "Session analysis runs as a FastAPI background task and stores in-memory demo results through `services/session_store.py`.",
            ]
        ),
        p("Request Flow", "h2"),
        p(
            "User action in React -> Axios API client -> FastAPI router -> Supabase token verification -> service layer -> result/status response -> React polling or results display.",
        ),
        p("Environment Flow", "h2"),
        bullets(
            [
                "Frontend variables use the `VITE_` prefix because Vite exposes only prefixed variables to browser code.",
                "Backend variables are loaded by Pydantic Settings from `pitchly-backend/.env`.",
                "Production CORS is controlled by `CORS_ORIGINS`, allowing a deployed frontend URL to call the API.",
            ]
        ),
        PageBreak(),
    ]

    story += [
        p("2. Frontend Code", "h1"),
        p(
            "The frontend is a TypeScript React single page app. It is built by Vite and served locally at `http://localhost:5173`.",
        ),
        table(
            [
                ["File or Folder", "Role"],
                ["pitchly/src/main.tsx", "Application bootstrap. It mounts React into `#root` and renders `App` inside `StrictMode`."],
                ["pitchly/src/App.tsx", "Defines all client routes and wraps the app with `AuthProvider`."],
                ["pitchly/src/auth/*", "Auth context, auth service, route protection, and hooks for consuming logged-in user state."],
                ["pitchly/src/pages/*", "Full page screens: home, dashboard, mode selection, setup, session recording, processing, results, and auth pages."],
                ["pitchly/src/components/layout/*", "Reusable page shell, sidebar, and top bar components."],
                ["pitchly/src/components/ui/*", "Reusable visual controls such as buttons, inputs, cards, modal, badges, skeletons, and password strength."],
                ["pitchly/src/components/webcam/*", "Camera preview and recording controls used during practice sessions."],
                ["pitchly/src/components/feedback/*", "Feedback visualization components such as score cards, radar chart, and feedback panels."],
                ["pitchly/src/hooks/*", "Reusable hooks for recording, session state, and polling backend status."],
                ["pitchly/src/services/api.ts", "Central Axios API client. Adds Supabase bearer token to backend calls."],
                ["pitchly/src/lib/supabase.ts", "Creates the Supabase browser client from Vite environment variables."],
                ["pitchly/src/lib/api.ts", "Small helper to build backend API URLs."],
                ["pitchly/src/constants/index.ts", "Shared app constants."],
                ["pitchly/src/index.css and App.css", "Global and app-level styling."],
                ["pitchly/public/*", "Static browser assets such as favicon, icons, and deployment redirects."],
            ],
            [2.2 * inch, 4.8 * inch],
        ),
        p("Frontend API Methods", "h2"),
        bullets(
            [
                "`analyzeSession` starts a backend session analysis job.",
                "`uploadVideo` sends a recorded video file for a specific session.",
                "`getStatus` checks background job progress.",
                "`getResults` fetches analysis output for a session.",
                "`getDashboard` loads dashboard data for the current user.",
            ]
        ),
        PageBreak(),
    ]

    story += [
        p("3. Navigation Map", "h1"),
        p("Navigation is defined in `pitchly/src/App.tsx`. Public routes are available to everyone. Protected routes require a valid Supabase session."),
        table(
            [
                ["Route", "Screen", "Access", "Purpose"],
                ["/", "Home", "Public", "Landing/start screen for the application."],
                ["/login", "Login", "Public", "Sign in with Supabase credentials."],
                ["/signup", "SignUp", "Public", "Create an account."],
                ["/forgot-password", "ForgotPassword", "Public", "Request password reset email."],
                ["/reset-password", "ResetPassword", "Public", "Set a new password after reset."],
                ["/verify-email", "VerifyEmail", "Public", "Email verification flow."],
                ["/dashboard", "Dashboard", "Protected", "Shows user practice activity and dashboard metrics."],
                ["/modes", "ModeSelection", "Protected", "Choose the type of practice session."],
                ["/interview-setup", "InterviewSetup", "Protected", "Configure interview practice."],
                ["/social-setup", "SocialSetup", "Protected", "Configure social speaking practice."],
                ["/session", "Session", "Protected", "Record or run the active practice session."],
                ["/processing", "Processing", "Protected", "Wait for background analysis."],
                ["/results/:sessionId", "Results", "Protected", "Show scores and feedback for a completed session."],
                ["*", "Navigate to /", "Fallback", "Unknown routes redirect home."],
            ],
            [1.25 * inch, 1.35 * inch, 0.9 * inch, 3.5 * inch],
        ),
        p("Typical User Journey", "h2"),
        p(
            "Home -> signup/login -> dashboard -> modes -> setup -> session recording -> processing -> results.",
        ),
        PageBreak(),
    ]

    story += [
        p("4. Backend Code", "h1"),
        p(
            "The backend is a FastAPI app served locally with Uvicorn and deployable with Gunicorn plus the Uvicorn worker. Its local URL is `http://localhost:8000`.",
        ),
        table(
            [
                ["File or Folder", "Role"],
                ["pitchly-backend/main.py", "Creates the FastAPI app, configures CORS, includes routers, and exposes `/health`."],
                ["pitchly-backend/app/config.py", "Typed environment settings loaded from `.env`, including Supabase, database, and CORS settings."],
                ["pitchly-backend/app/auth.py", "Verifies Supabase bearer tokens for protected endpoints."],
                ["pitchly-backend/app/supabase_client.py", "Creates a cached Supabase admin client using the service role key."],
                ["pitchly-backend/app/storage.py", "Validates video uploads, writes to Supabase Storage, and creates signed URLs."],
                ["pitchly-backend/routers/auth.py", "Receives protected auth event logs."],
                ["pitchly-backend/routers/session.py", "Starts analysis jobs and exposes job status."],
                ["pitchly-backend/routers/upload.py", "Receives session video upload files."],
                ["pitchly-backend/routers/results.py", "Returns analysis results for a session."],
                ["pitchly-backend/routers/dashboard.py", "Returns dashboard data for the current user."],
                ["pitchly-backend/services/session_store.py", "In-memory session, job, dashboard, and demo result storage."],
                ["pitchly-backend/services/analysis_pipeline.py", "Background analysis pipeline. Currently creates demo results after a short delay."],
                ["pitchly-backend/schemas/session.py", "Pydantic request models for session creation."],
                ["pitchly-backend/migrations/*", "Alembic database migration files for the Supabase/Postgres schema."],
                ["pitchly-backend/requirements.txt", "Pinned Python dependencies for local and production installs."],
            ],
            [2.25 * inch, 4.75 * inch],
        ),
        p("Backend Health Check", "h2"),
        code("GET /health -> returns status, environment, and active Supabase storage bucket."),
        PageBreak(),
    ]

    story += [
        p("5. How Core Features Work", "h1"),
        p("Authentication", "h2"),
        bullets(
            [
                "The frontend uses Supabase browser authentication from `pitchly/src/lib/supabase.ts`.",
                "Protected pages are wrapped in `ProtectedRoute`, so unauthenticated users cannot access core app screens.",
                "Backend calls include `Authorization: Bearer <token>` through the Axios interceptor.",
                "The backend validates the token in `app/auth.py` using the Supabase admin client.",
            ]
        ),
        p("Session Recording and Upload", "h2"),
        bullets(
            [
                "The session screen uses webcam and recorder components to capture video.",
                "The upload API sends a `FormData` payload to `/upload/{sessionId}`.",
                "The backend checks content type and max file size before writing to Supabase Storage.",
                "Stored videos receive signed URLs for controlled access.",
            ]
        ),
        p("Analysis and Results", "h2"),
        bullets(
            [
                "The frontend calls `/session/analyze` to create a session and background job.",
                "FastAPI `BackgroundTasks` runs `run_analysis_pipeline` without blocking the HTTP response.",
                "The current pipeline writes demo results through `create_demo_result`.",
                "The frontend polls `/session/status/{jobId}` and then navigates to `/results/{sessionId}`.",
            ]
        ),
        p("Important Runtime Limitation", "h2"),
        p(
            "The current backend stores sessions and jobs in memory through `session_store.py`. This works locally and for demos, but production persistence should move to Supabase/Postgres before relying on data surviving restarts or multiple backend instances.",
        ),
        PageBreak(),
    ]

    story += [
        p("6. Files Created or Changed for Local Run and Deployment", "h1"),
        table(
            [
                ["File", "What it represents"],
                ["README.md", "Top-level project guide with local setup, build, and deployment instructions."],
                ["render.yaml", "Render blueprint defining `pitchly-api` backend and `pitchly-web` static frontend services."],
                [".gitignore", "Ignores `.local/`, where local runtime logs can be written without dirtying git."],
                ["package.json", "Root workspace scripts for frontend install, backend install, frontend dev, backend dev, and build."],
                ["package-lock.json", "Updated root lock metadata to match the new root package name."],
                ["pitchly-backend/Procfile", "Generic production process command for hosts that use Procfile conventions."],
                ["pitchly-backend/runtime.txt", "Pins Python 3.11.9 for deployment platforms that read runtime files."],
                ["pitchly-backend/.env.example", "Documents `CORS_ORIGINS` in addition to existing backend environment variables."],
                ["pitchly-backend/app/config.py", "Adds `cors_origins` setting and `allowed_origins` parser."],
                ["pitchly-backend/main.py", "Uses parsed `settings.allowed_origins` for FastAPI CORS."],
                ["pitchly/.nvmrc", "Pins Node 20 for frontend deployments and developer machines using nvm."],
                ["pitchly/vercel.json", "SPA rewrite so Vercel serves React routes through `index.html`."],
                ["pitchly/public/_redirects", "SPA rewrite for Netlify-style static hosting."],
            ],
            [2.35 * inch, 4.65 * inch],
        ),
        p("Local Commands", "h2"),
        code("npm run install:frontend\nnpm run dev:backend\nnpm run dev:frontend\nnpm run build"),
        PageBreak(),
    ]

    story += [
        p("7. Deployment Guide", "h1"),
        p("Render Deployment", "h2"),
        bullets(
            [
                "Push the repository to GitHub.",
                "Create a Render Blueprint from the repository.",
                "Render reads `render.yaml` and creates both backend and frontend services.",
                "Set backend secrets on `pitchly-api` and frontend public Vite variables on `pitchly-web`.",
                "Set `VITE_API_URL` to the deployed backend URL.",
                "Set backend `CORS_ORIGINS` to the deployed frontend URL.",
                "Verify `https://your-backend-url/health`, then open the frontend URL.",
            ]
        ),
        p("Required Backend Variables", "h2"),
        code("GEMINI_API_KEY\nSUPABASE_URL\nSUPABASE_ANON_KEY\nSUPABASE_SERVICE_ROLE_KEY\nSUPABASE_STORAGE_BUCKET\nDATABASE_URL\nFRONTEND_URL\nCORS_ORIGINS\nENVIRONMENT=production"),
        p("Required Frontend Variables", "h2"),
        code("VITE_SUPABASE_URL\nVITE_SUPABASE_ANON_KEY\nVITE_API_URL"),
        p("Other Hosting Options", "h2"),
        p(
            "The backend can deploy to any Python web host that supports Gunicorn. The frontend can deploy to any static host that runs `npm ci && npm run build` and publishes `pitchly/dist`.",
        ),
        PageBreak(),
    ]

    story += [
        p("8. Maintenance Notes", "h1"),
        bullets(
            [
                "Keep `.env` files out of git because they contain secrets.",
                "Use `npm run build` before deploying frontend changes.",
                "Use `npm --prefix pitchly run lint` before committing frontend changes.",
                "Replace in-memory session storage with database-backed persistence for production scale.",
                "Connect `analysis_pipeline.py` to the real Gemini/video/audio analysis logic when ready.",
                "Keep `CORS_ORIGINS` explicit in production rather than using a wildcard.",
                "Use Supabase storage bucket permissions carefully because uploaded practice videos may be sensitive.",
            ]
        ),
        p("Quick Local Verification", "h2"),
        code("Backend: http://localhost:8000/health\nFrontend: http://localhost:5173"),
    ]

    doc.build(story)


if __name__ == "__main__":
    build()
