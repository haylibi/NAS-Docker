import logging
import sys
from flask import Flask
from src.utils import constants
from src.watched_tag import watched_tag_bp

def create_app():
    app = Flask(__name__)

    # --- LOGGER SETUP ---
    # Configure logging to output to stdout for Docker
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(constants.LOG_LEVEL)
    
    # Register blueprints
    app.register_blueprint(watched_tag_bp)

    app.logger.info(f"Jellyfin Webhooks Server started on port {constants.PORT}")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=constants.PORT)