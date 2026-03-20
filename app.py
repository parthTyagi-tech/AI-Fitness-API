import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import joblib
from dotenv import load_dotenv

from extensions import db, login_manager, oauth

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config['PREFERRED_URL_SCHEME'] = 'https'

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Add it to your .env file or deployment environment."
        )

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///database.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Google OAuth config ───────────────────────────────────────────────────
    app.config['GOOGLE_CLIENT_ID']     = os.environ.get('GOOGLE_CLIENT_ID', '')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    # ── Load ML model once at startup ────────────────────────────────────────
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'gym_ai_bodyfat_model.pkl')
    try:
        app.config['MODEL'] = joblib.load(model_path)
    except FileNotFoundError:
        raise RuntimeError(
            f"ML model not found at '{model_path}'. "
            "Make sure gym_ai_bodyfat_model.pkl is inside a 'models/' folder."
        )

    # ── Extensions ───────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

    # ── User loader ───────────────────────────────────────────────────────────
    from db_models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Blueprints ────────────────────────────────────────────────────────────
    from routes import main
    app.register_blueprint(main)

    # ── Create tables ─────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    flask_app = create_app()
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    flask_app.run(debug=debug_mode)
