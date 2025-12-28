import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from jellyfin_webhooks.utils.constants import constants as c

from jellyfin_webhooks import api as api_routes
from jellyfin_webhooks import webhook as webhook_routes

# Configure Logging
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    # Define possible paths for the frontend build
    # 1. Docker Production (Separate folder to avoid volume mount overwrite)
    # 2. Local Development (Relative to this file)
    possible_paths = [
        "/app/frontend_static",
        os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"),
        os.path.join(os.path.dirname(__file__), "static", "react")
    ]
    
    static_folder = None
    for path in possible_paths:
        if os.path.exists(path):
            static_folder = path
            break
            
    if not static_folder:
        print(f"WARNING: Frontend build not found in any of: {possible_paths}")
        # Fallback to avoid crash, though 404s will occur
        static_folder = os.path.join(os.path.dirname(__file__), "static", "react")
    
    # We set static_folder to None initially to avoid conflicts with default Flask static serving
    app = Flask(__name__, static_folder=None)
    CORS(app)

    # Create a rotating file handler
    handler = RotatingFileHandler(c.LOG_FILE, maxBytes=c.MAX_LOG_SIZE, backupCount=1)
    handler.setLevel(logging.INFO if not c.DEBUG_ENVIRONMENT else logging.DEBUG)
    
    # Create a formatter
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    
    # Add handler to the ROOT logger so we capture Flask, libraries, etc.
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO if not c.DEBUG_ENVIRONMENT else logging.DEBUG)
    
    # Also ensure Flask app logger propagates or has the handler (usually redundant if root has it, but safe)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO if not c.DEBUG_ENVIRONMENT else logging.DEBUG)

    # Register API Blueprints
    app.register_blueprint(webhook_routes.playback_stop.route)
    app.register_blueprint(webhook_routes.stremio_event.route)
    
    app.register_blueprint(api_routes.logs.route)
    app.register_blueprint(api_routes.webhooks.route)
    app.register_blueprint(api_routes.torrents.route)
    app.register_blueprint(api_routes.requests.route)

    # --- SERVE REACT FRONTEND ---
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        # 1. Try serving the path exactly as requested
        full_path = os.path.join(static_folder, path)
        if path != "" and os.path.exists(full_path):
            return send_from_directory(static_folder, path)

        # 2. Try stripping the Base URL if configured
        if c.BASE_URL and path.startswith(c.BASE_URL.strip('/')):
            stripped = path.replace(c.BASE_URL.strip('/'), '', 1).lstrip('/')
            if stripped and os.path.exists(os.path.join(static_folder, stripped)):
                return send_from_directory(static_folder, stripped)

        # 3. Fallback: specific fix for hardcoded vite base 'jellyfin-webhooks' if not covered above
        if path.startswith('jellyfin-webhooks/'):
            stripped = path.replace('jellyfin-webhooks/', '', 1)
            if stripped and os.path.exists(os.path.join(static_folder, stripped)):
                return send_from_directory(static_folder, stripped)

        # Default to index.html for SPA routing
        return send_from_directory(static_folder, 'index.html')

    return app

if __name__ == '__main__':
    if os.getenv('ENABLE_DEBUGPY', 'false').lower() == 'true':
        print("Waiting for debugger to attach on port 5678...")
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        # Optional: block until attached
        # debugpy.wait_for_client()
        print("Debugger attached!")

    app = create_app()
    print(f"DEBUG: BASE_URL is '{c.BASE_URL}'")
    print("DEBUG: Registering Rules:")
    print(app.url_map)
    app.run(host='0.0.0.0', port=c.PORT, debug=c.DEBUG_ENVIRONMENT) # Important: turn off Flask debug reloader if using debugpy