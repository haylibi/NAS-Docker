import qbittorrentapi
from flask import Blueprint, request, current_app, jsonify
from jellyfin_webhooks.utils.constants import constants as c
from jellyfin_webhooks.utils.decorators import log_request
from jellyfin_webhooks.components.series import Series
from jellyfin_webhooks.components.movie import Movie


route = Blueprint('playback_stop', __name__)

@route.route(f'{c.BASE_URL}/webhook/playback_stop', methods=['POST'])
@log_request(category="webhook", endpoint="playback_stop")
def main():
    # Always pull fresh settings to check if enabled
    if not c.settings.get('playback_stop', {}).get('enabled'):
        current_app.logger.info("Received /tagger request but webhook is currently DISABLED.")
        return jsonify({"status": "disabled"}), 200

    data = request.json
    dry_run = request.args.get('dry_run', 'false').lower() == 'true' or data.get('dry_run', False)
    
    should_process = (data.get('NotificationType') == 'PlaybackStop' and data.get('PlayedToCompletion', False)) or dry_run

    if not should_process:
        return jsonify({"status": "ignored", "reason": "Not a watched event"}), 200

    torrent_file_path = None
    last_ep_torrent_file_path = None
    if data.get('ItemType') == 'Episode':
        season = Series(
            name=data.get('SeriesName'),
            base_dir = f'/data/media/series/{data.get("SeriesName")}'
        )[int(data.get('SeasonNumber'))]
        torrent_file_path = season[data.get('EpisodeNumber')].get_torrent_path()
        assert torrent_file_path is not None, 'Could not proceed with request. Server was unable to find torrent file corresponding to Episode'

        # Must verify if Episode is part of a `Series Pack`. 
        #   This is done by checking all episodes, and comparing the torrent file path of the latest episode
        #   With the torrents (if both `watched` ep and `last` ep have similar root (base-dir), they're a season pack)
        last_ep_torrent_file_path = season[-1].get_torrent_path()
        if last_ep_torrent_file_path == torrent_file_path:
            last_ep_torrent_file_path = None    # If `watched` == `last_ep`, then proceed normally (so tag torrent as watched either way)
    else:
        movie = Movie(
            name=data.get('Name'),
            base_dir = f'/data/media/movies/{data.get("Name")} ({data.get("PremiereDate").split("-")[0]})'.replace(':', ' -')
        )
        torrent_file_path = movie.get_torrent_path()
    
    assert torrent_file_path is not None, 'Cannot proceed with torrent_file_path as None'

    # If dry_run is True and we have a media_name, it might be a manual test
    log_prefix = "[DRY RUN]" if dry_run else "[LIVE]"
    
    # Get played Percentage
    position_ticks = int(data.get('PlaybackPositionTicks', 0) or 0)
    total_ticks = int(data.get('RunTimeTicks', 0) or 1) # avoid divide by zero
    played_percentage = (position_ticks / total_ticks) * 100

    current_app.logger.info(f"{log_prefix} Processing watched event for: {data.get('Name', '')} (Watched {int(played_percentage)}%)")
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
        message = ''
        for torrent in torrents:
            if torrent.content_path.lower() not in torrent_file_path.as_posix().lower():
                continue

            # Check if torrent path is also root of `last_ep`
            if last_ep_torrent_file_path and torrent.content_path.lower() in last_ep_torrent_file_path.as_posix().lower():
                found = True
                message = 'Episode is part of a Series Pack, can only tag as watched on series last episode.'
                break
                
            # Check if they match, otherwise
            if not dry_run:
                torrent.add_tags(tags='watched')
                current_app.logger.info(f"SUCCESS: Tagged {torrent.name} as 'watched'")
            else:
                current_app.logger.info(f"DRY RUN: Found match {torrent.name}")
            
            tagged_torrents.append(torrent.name)
            found = True
        
        if not found:
            current_app.logger.warning(f"No torrent found matching name: {data.get('Name', '')}")
            
        return jsonify({
            "status": "success",
            "dry_run": dry_run,
            "tagged_torrents": tagged_torrents,
            "match_found": found,
            "message": message
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"Error connecting to qBittorrent: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
