from flask import Blueprint, jsonify, current_app
import qbittorrentapi
from jellyfin_webhooks.utils.constants import constants as c
from jellyfin_webhooks.utils.decorators import log_request

route = Blueprint('api_torrents', __name__)

@route.route(f'{c.BASE_URL}/api/torrents', methods=['GET'])
@log_request(category="api", endpoint="torrents")
def get_torrents():
    try:
        qbt_client = qbittorrentapi.Client(
            host=c.QBT_HOST, 
            username=c.QBT_USER, 
            password=c.QBT_PASS
        )
        qbt_client.auth_log_in()
        
        torrents = qbt_client.torrents_info()
        
        # Simplify the response
        results = []
        for t in torrents:
            results.append({
                "name": t.name,
                "hash": t.hash,
                "size": t.size,
                "state": t.state,
                "progress": t.progress
            })
            
        # Sort by name
        results.sort(key=lambda x: x['name'].lower())
            
        return jsonify({
            "status": "success",
            "data": results
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching torrents: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
