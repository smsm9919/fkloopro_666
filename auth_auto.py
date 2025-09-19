# auth_auto.py — Auto-register auth endpoints
import sys, importlib
from flask import request, jsonify
from werkzeug.security import check_password_hash

def init(app):
    def _get_login_funcs():
        try:
            from flask_login import login_user, logout_user, current_user
            return login_user, logout_user, current_user
        except Exception:
            return None, None, None

    def _get_db():
        try:
            from flask import current_app
            db_ext = current_app.extensions.get("sqlalchemy")
            if db_ext and hasattr(db_ext, "db"):
                return db_ext.db
        except Exception:
            pass
        try:
            app_mod = importlib.import_module("app")
            return getattr(app_mod, "db", None)
        except Exception:
            return None

    def _get_user_model():
        for mod_name in ("models", "app"):
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, "User"):
                    return getattr(mod, "User")
            except Exception:
                continue
        return None

    @app.get("/auth/health")
    def health():
        return jsonify(ok=True)

    @app.post("/auth/login")
    def login():
        data = request.get_json(silent=True) or request.form
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify(ok=False, error="email and password required"), 200

        User = _get_user_model()
        db = _get_db()
        login_user, _, _ = _get_login_funcs()

        if not (User and db and login_user):
            return jsonify(ok=False, error="auth backend not fully configured"), 200

        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify(ok=False, error="invalid credentials"), 200
            if not check_password_hash(user.password, password):
                return jsonify(ok=False, error="invalid credentials"), 200
            login_user(user)
            return jsonify(ok=True)
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 200

    @app.post("/auth/logout")
    def logout():
        try:
            from flask_login import logout_user
            logout_user()
        except Exception:
            pass
        return jsonify(ok=True)

# Auto-attach
try:
    import app as _app_mod
    app = getattr(_app_mod, "app", None)
    if app:
        init(app)
except Exception as e:
    sys.stderr.write(f"[auth_auto] could not attach: {e}\n")