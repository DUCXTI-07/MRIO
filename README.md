# ⚙️ Manufacturing Manual Assistant (Nexus Four)

An enterprise-grade, role-protected RAG (Retrieval-Augmented Generation) maintenance assistant built for industrial equipment troubleshooting, technical manual querying, and secure supervisory oversight.

---

## 🚀 Key Features

* **Machine-Isolated RAG Pipeline**: Ensures queries regarding specific machinery only retrieve embeddings and text chunks from authorized equipment manuals, eliminating cross-contamination of technical data.
* **Strict Role-Based Access Control (RBAC)**:
  * **Administrators**: Authorized to register equipment and upload official PDF manuals.
  * **Engineers**: Permitted to query isolated manual embeddings and receive precise answers with page citations.
  * **Supervisors**: Full audit log and question history inspection via secure REST endpoints.
* **High-Performance Ingestion Engine**: Powered by PyMuPDF (`fitz`) for lightning-fast text extraction, chunking, and metadata indexing from complex industrial PDFs.
* **Production-Ready Architecture**: Configured with WhiteNoise static file compression, environment-variable security, and Docker/Gunicorn container support.
* **Interactive Responsive Dashboard**: Clean, modern Bootstrap 5 web UI featuring dynamic API-driven machine selection, manual inspection panels, and real-time query responses.

---

## 🛠️ Tech Stack

* **Backend & API**: Django 6.1, Django REST Framework (DRF)
* **Database**: SQLite (Development) / PostgreSQL (Production)
* **Document Processing**: PyMuPDF (`fitz`)
* **Deployment & Serving**: Gunicorn, WhiteNoise, Docker, Render / Railway compatible
* **Frontend**: HTML5, Bootstrap 5, JavaScript (Async Fetch API)

---

## 🚀 Deploying to Render

1. Connect this repository to Render and choose **Blueprint** deployment so it
   reads `render.yaml`.
2. Render provisions the web service and PostgreSQL database. The blueprint
   generates `DJANGO_SECRET_KEY`; do not replace it with a committed secret.
3. Wait for the first deployment to finish, then open the service URL and create
   an account using the sign-up page.

The web process applies database migrations at startup and serves collected
static files with WhiteNoise. For local development, set `DJANGO_SECRET_KEY`
and `DJANGO_DEBUG=True` before running `python manage.py runserver`.
Set `GEMINI_API_KEY` in the Render service environment to enable Gemini answers;
without it, the app uses its local machine-isolated manual retrieval.

---

## 📂 Project Structure

```text
manual_assistant/
│
├── core/                        # Core application module
│   ├── migrations/              # Database migrations
│   ├── templates/core/          # Frontend templates (dashboard, manage, supervisor)
│   ├── models.py                # Relational data models (Machine, Manual, DocumentChunk, QuestionRecord)
│   ├── views.py                 # API endpoints and dashboard views
│   ├── permissions.py           # Custom RBAC permission classes
│   └── tests.py                 # Automated test suite
│
├── manual_assistant/            # Django project settings and WSGI configuration
│   ├── settings.py              # Production-ready configuration (WhiteNoise, Env vars)
│   ├── urls.py                  # Root URL router
│   └── wsgi.py                  # WSGI application entry point
│
├── staticfiles/                 # Collected production static assets
├── Dockerfile                   # Container definition for cloud deployment
├── requirements.txt             # Python dependencies
└── manage.py                    # Django management utility
