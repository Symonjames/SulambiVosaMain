from flask import Flask, send_from_directory, request
from flask_cors import CORS
from app.blueprint import ApiBlueprint
from app.config.cors_and_cookies import get_cors_origins
from dotenv import load_dotenv
import sys
import os

load_dotenv()

def testFunction():
  import data.automation.eventTableMigrator

# Create Flask app (needed for both dev and production)
Server = Flask(__name__)

# CORS: specific origins only (never "*") when using credentials (session cookie).
# Set FRONTEND_URL on Render: https://www.sulambi-vosa.com
allowed_origins = get_cors_origins()

def is_allowed_origin(origin):
    """True if origin is in the allowed list (required for credentials)."""
    if not origin:
        return False
    if origin in allowed_origins:
        return True
    if origin.endswith(".onrender.com"):
        return True
    if "sulambi-vosa.com" in origin:
        return True
    return False

# Credentials = true → must use specific origins, never "*"
CORS(Server,
     resources={r"/*": {
         "origins": allowed_origins,
         "allow_headers": ["Content-Type", "Authorization"],
         "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
         "supports_credentials": True,
         "expose_headers": "*",
     }},
     supports_credentials=True)

# Handle CORS preflight (OPTIONS) requests explicitly
@Server.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        from flask import jsonify, make_response
        origin = request.headers.get('Origin')
        if is_allowed_origin(origin):
            response = make_response(jsonify({"status": "ok"}), 200)
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
        else:
            # Log blocked origin for debugging
            print(f"[CORS] Blocked preflight request from origin: {origin}")
            return make_response(jsonify({"error": "Origin not allowed"}), 403)

# Add CORS headers to all responses (including errors). Never use "*" when credentials=True.
@Server.after_request
def after_request(response):
    origin = request.headers.get("Origin", "")
    if origin and is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
    # If no origin or not allowed, do not set Allow-Origin (browser will block; avoid wrong origin)
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Handle errors and ensure CORS headers are set even on exceptions
@Server.errorhandler(Exception)
def handle_error(error):
    from flask import jsonify
    origin = request.headers.get('Origin', '') if request else ''
    response = jsonify({
        'message': str(error),
        'error': type(error).__name__
    })
    response.status_code = 500 if not hasattr(error, 'code') else error.code
    
    # CORS on errors: only set origin when allowed (never "*" when credentials used)
    if origin and is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@Server.route("/uploads/<path:path>")
def staticFileHost(path):
  response = send_from_directory("uploads", path)
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'GET'
  response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
  response.headers['Cache-Control'] = 'public, max-age=3600'
  return response

Server.register_blueprint(ApiBlueprint)

# Run migration to add beneficiaryEvaluationPin column if missing (e.g. on Render)
try:
  from app.database.migrate_beneficiary_pin import run_beneficiary_pin_migration
  run_beneficiary_pin_migration()
except Exception as e:
  print(f"[startup] migrate_beneficiary_pin: {e}")

# Export app for Gunicorn (production)
app = Server

if __name__ == "__main__":
  if ("--init" in sys.argv):
    import app.database.tableInitializer
    exit()
  if ("--migrate-photo-captions" in sys.argv):
    from app.database.migrate_photo_captions import migrate_photo_captions
    migrate_photo_captions()
    exit()
  if ("--test" in sys.argv):
    testFunction()
    exit()
  if ("--reset" in sys.argv):
    if (os.path.isfile(os.getenv("DB_PATH"))):
      os.remove(os.getenv("DB_PATH"))
    exit()

  # Use environment variables for production, defaults for development
  host = os.getenv("HOST", "localhost")
  port = int(os.getenv("PORT", 8000))
  
  # Run Flask dev server (only in development)
  Server.run(host=host, port=port, debug=True)