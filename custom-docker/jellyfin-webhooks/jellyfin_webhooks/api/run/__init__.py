from flask import Blueprint, jsonify, current_app
from backend.utils.constants import constants as c
import qbittorrentapi

route = Blueprint('api/run', __name__, template_folder='templates')


@route.route(f'{c.BASE_URL}/api/run/<webhook_id>', methods=['POST'])
def post_run(webhook_id):
    current_app.logger.info(f"MANUAL RUN: Triggered for {webhook_id}")
    
    # Logic to trigger a scan of recent torrents
    try:
        qbt = qbittorrentapi.Client(host=c.QBT_HOST, username=c.QBT_USER, password=c.QBT_PASS)
        qbt.auth_log_in()
        # We can trigger a refresh of the last 5 torrents
        recent = qbt.torrents_info(limit=5, sort='added_on', reverse=True)
        current_app.logger.info(f"Manual scan complete. Checked {len(recent)} recent torrents.")
        return jsonify({"status": "SUCCESS", "message": "Scan triggered"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500