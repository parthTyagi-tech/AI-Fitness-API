import os
import sys
import logging
from contextlib import asynccontextmanager
import joblib
from dotenv import load_dotenv

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from database import init_db
from routes import router as main_router
from auth import NotAuthenticatedException
from templates import render_template, flash

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_fitness")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Database Initialization ──────────────────────────────────────────────
    try:
        init_db()
    except Exception as e:
        logger.error("Database initialization failed during startup: %s", e)

    # ── Load ML Model ────────────────────────────────────────────────────────
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'gym_ai_bodyfat_model.pkl')
    if not os.path.exists(model_path):
        raise RuntimeError(
            f"ML model not found at '{model_path}'. "
            "Make sure gym_ai_bodyfat_model.pkl is inside a 'models/' folder."
        )
    app.state.model = joblib.load(model_path)
    logger.info("ML model loaded successfully from %s", model_path)

    yield


def create_app() -> FastAPI:
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Add it to your .env file or deployment environment."
        )

    app = FastAPI(
        title="AI Driven Fitness Intelligence System",
        description="FastAPI-powered biometric body fat prediction and personalized workout engine",
        lifespan=lifespan,
    )
    app.state.secret_key = secret_key

    # ── Load ML Model eagerly ────────────────────────────────────────────────
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'gym_ai_bodyfat_model.pkl')
    if not os.path.exists(model_path):
        raise RuntimeError(
            f"ML model not found at '{model_path}'. "
            "Make sure gym_ai_bodyfat_model.pkl is inside a 'models/' folder."
        )
    app.state.model = joblib.load(model_path)

    # ── Session Middleware ───────────────────────────────────────────────────
    app.add_middleware(
        SessionMiddleware,
        secret_key=secret_key,
        session_cookie="ai_fitness_session",
        max_age=86400 * 14,  # 14 days
        same_site="lax",
        https_only=False,
    )

    # ── Static Files ─────────────────────────────────────────────────────────
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # ── Include Routers ──────────────────────────────────────────────────────
    app.include_router(main_router)

    # ── Exception Handlers ───────────────────────────────────────────────────
    @app.exception_handler(NotAuthenticatedException)
    async def not_authenticated_handler(request: Request, exc: NotAuthenticatedException):
        flash(request, "Please log in to access this page.", "info")
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return render_template(request, '404.html', status_code=404)

    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc):
        logger.exception("Internal Server Error: %s", exc)
        return render_template(request, '500.html', status_code=500)

    return app


app = create_app()


# ── Entry point & CLI ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        init_db()
        print("Database initialized successfully.")
        sys.exit(0)

    is_development = os.environ.get('FLASK_ENV', '').lower() == 'development' or \
                     os.environ.get('ENVIRONMENT', '').lower() == 'development'
    debug_flag = os.environ.get('DEBUG', 'false').lower() == 'true'
    debug_mode = is_development and debug_flag

    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1' if debug_mode else '0.0.0.0')

    uvicorn.run("app:app", host=host, port=port, reload=debug_mode)
