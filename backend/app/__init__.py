import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def _get_cors_origins():
    origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
    if origins == "*":
        return origins
    return [o.strip() for o in origins.split(",") if o.strip()]

# PUBLIC_INTERFACE
def create_app():
    """Create and configure the Flask application.
    Returns:
        Flask: Configured Flask app with DB, blueprints, CORS, and error handlers.
    """
    from .config import Config
    from .errors import register_error_handlers

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={r"/api/*": {"origins": _get_cors_origins()}}, supports_credentials=True)

    # Register blueprints
    from .routes_auth import bp as auth_bp
    from .routes_models import bp as models_bp
    from .routes_mappings import bp as mappings_bp
    from .routes_provision import bp as provision_bp
    from .routes_admin import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(models_bp, url_prefix="/api")
    app.register_blueprint(mappings_bp, url_prefix="/api")
    app.register_blueprint(provision_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Health endpoint
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    register_error_handlers(app)
    return app

# Import models after db for migrations
from . import models  # noqa: E402
