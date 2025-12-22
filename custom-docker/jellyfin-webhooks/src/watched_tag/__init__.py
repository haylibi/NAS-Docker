from flask import Blueprint, request, current_app
import qbittorrentapi
from src.utils import constants

watched_tag_bp = Blueprint('watched_tag', __name__)

@watched_tag_bp.route('/tagger', methods=['POST'])
def jellyfin_tagger():
    data = request.json
    
    # Logic: Only tag if Playback Stop + >90% watched
    if data.get('NotificationType') == 'PlaybackStop' and data.get('PlayedPercentage', 0) > 90:
        media_name = data.get('Name')
        current_app.logger.info(f"Processing watched event for: {media_name}")

        try:
            qbt_client = qbittorrentapi.Client(
                host=constants.QBT_HOST, 
                username=constants.QBT_USER, 
                password=constants.QBT_PASS
            )
            qbt_client.auth_log_in()
            
            torrents = qbt_client.torrents_info()
            found = False
            for torrent in torrents:
                if media_name.lower() in torrent.name.lower():
                    torrent.add_tags(tags='watched')
                    current_app.logger.info(f"SUCCESS: Tagged {torrent.name} as 'watched'")
                    found = True
            
            if not found:
                current_app.logger.warning(f"No torrent found matching name: {media_name}")
                
        except Exception as e:
            current_app.logger.error(f"Error connecting to qBittorrent: {e}")

    return "OK", 200