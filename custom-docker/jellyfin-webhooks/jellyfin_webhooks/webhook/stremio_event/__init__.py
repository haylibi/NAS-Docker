from flask import Blueprint, request, current_app
from jellyfin_webhooks.utils.constants import constants as c
from jellyfin_webhooks.utils.decorators import log_request

route = Blueprint('stremio', __name__)

@route.route(f'{c.BASE_URL}/webhook/stremio-event', methods=['POST'])
@log_request(category="webhook", endpoint="stremio-event")
def handle_stremio():
    data = request.json
    current_app.logger.info(f"Stremio Signal Received: {data.get('event')}")
    
    # Add your custom logic here (e.g. notify Discord when someone uses Stremio)
    return "OK", 200