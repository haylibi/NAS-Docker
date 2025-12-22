from flask import Blueprint, jsonify
from jellyfin_webhooks.utils.constants import constants as c

route = Blueprint('api_webhooks', __name__)

@route.route(f'{c.BASE_URL}/api/webhooks')
def get_webhooks():
    # Convert dictionary to list for frontend
    webhooks_list = []
    for key, config in c.settings.items():
        webhooks_list.append({
            "id": key,
            "name": config.get("name", key),
            "description": config.get("description", ""),
            "enabled": config.get("enabled", False),
            "endpoint": config.get("endpoint", "")
        })
    
    return jsonify({
        "data": webhooks_list
    })
