# imgbb_auto.py — Auto-register ImgBB upload route
import os, requests, sys
from flask import request, jsonify

def init(app):
    ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_SIZE_MB = 10

    def _allowed(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

    @app.post("/upload")
    def upload_imgbb():
        api_key = os.getenv("IMGBB_API_KEY")
        if not api_key:
            return jsonify(ok=False, error="IMGBB_API_KEY not set"), 200

        files, data = None, None
        if "file" in request.files:
            f = request.files["file"]
            if not f or not f.filename:
                return jsonify(ok=False, error="empty filename"), 200
            if not _allowed(f.filename):
                return jsonify(ok=False, error="unsupported file type"), 200
            cl = request.content_length or 0
            if cl and cl > MAX_SIZE_MB * 1024 * 1024:
                return jsonify(ok=False, error="file too large"), 200
            files = {"image": (f.filename, f.stream, f.mimetype)}
        else:
            payload = request.get_json(silent=True) or {}
            b64 = payload.get("image_base64")
            if not b64:
                return jsonify(ok=False, error="no file or image_base64 provided"), 200
            if "," in b64 and "base64" in b64:
                b64 = b64.split(",", 1)[1]
            data = {"image": b64}

        try:
            resp = requests.post("https://api.imgbb.com/1/upload", params={"key": api_key}, files=files, data=data, timeout=30)
            js = resp.json()
            if resp.status_code == 200 and js.get("data", {}).get("url"):
                d = js["data"]
                return jsonify(ok=True, url=d.get("url"), delete_url=d.get("delete_url"), id=d.get("id"))
            return jsonify(ok=False, status=resp.status_code, error=js), 200
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 200

# Auto-attach
try:
    import app as _app_mod
    app = getattr(_app_mod, "app", None)
    if app:
        init(app)
except Exception as e:
    sys.stderr.write(f"[imgbb_auto] could not attach: {e}\n")