from flask import Blueprint, request, current_app, jsonify
import qbittorrentapi
from jellyfin_webhooks.utils.constants import constants as c

add_watched_tag = Blueprint('add_watched_tag', __name__)

@add_watched_tag.route(f'{c.BASE_URL}/webhook/add_watched_tag', methods=['POST'])
def main():
    # Always pull fresh settings to check if enabled
    if not c.settings.get('add_watched_tag', {}).get('enabled'):
        current_app.logger.info("Received /tagger request but webhook is currently DISABLED.")
        return jsonify({"status": "disabled"}), 200

    data = request.json
    dry_run = request.args.get('dry_run', 'false').lower() == 'true' or data.get('dry_run', False)
    
    # Logic: Only tag if Playback Stop + >90% watched
    # For dry_run, we process it regardless of events to test connectivity/matching
    should_process = (data.get('NotificationType') == 'PlaybackStop' and data.get('PlayedPercentage', 0) > 90) or dry_run

    if should_process:
        media_name = data.get('Name', '')
        
        # If dry_run is True and we have a media_name, it might be a manual test
        log_prefix = "[DRY RUN]" if dry_run else "[LIVE]"
        current_app.logger.info(f"{log_prefix} Processing watched event for: {media_name}")
        
        tagged_torrents = []
        
        try:
            qbt_client = qbittorrentapi.Client(
                host=c.QBT_HOST, 
                username=c.QBT_USER, 
                password=c.QBT_PASS
            )
            qbt_client.auth_log_in()
            
            torrents = qbt_client.torrents_info()
            found = False
            for torrent in torrents:
                if media_name.lower() in torrent.name.lower():
                    if not dry_run:
                        torrent.add_tags(tags='watched')
                        current_app.logger.info(f"SUCCESS: Tagged {torrent.name} as 'watched'")
                    else:
                        current_app.logger.info(f"DRY RUN: Found match {torrent.name}")
                    
                    tagged_torrents.append(torrent.name)
                    found = True
            
            if not found:
                current_app.logger.warning(f"No torrent found matching name: {media_name}")
                
            return jsonify({
                "status": "success",
                "dry_run": dry_run,
                "tagged_torrents": tagged_torrents,
                "match_found": found
            }), 200
                
        except Exception as e:
            current_app.logger.error(f"Error connecting to qBittorrent: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "ignored", "reason": "Not a watched event"}), 200