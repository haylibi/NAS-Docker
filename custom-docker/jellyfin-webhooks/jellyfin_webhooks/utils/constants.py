import os
import json


class Constants:
    QBT_HOST = os.getenv('QBT_HOST', 'http://gluetun:8080')
    QBT_USER = os.getenv('QBT_USER', 'admin')
    QBT_PASS = os.getenv('QBT_PASS', 'adminadmin')
    PORT = int(os.getenv('PORT', 5000))
    LOG_FILE = os.getenv('JELYFIN_WEBHOOKS_LOG_FILE', "/app/data/app.log")
    MAX_LOG_SIZE = int(os.getenv('MAX_LOG_SIZE', 10 * 1024 * 1024)) # 10MB default
    LOG_LEVEL = 0
    SETTINGS_FILE = os.getenv('JELYFIN_WEBHOOKS_SETTINGS_FILE', "/app/data/settings.json")
    DEBUG_ENVIRONMENT = os.getenv('JELLYFIN_WEBHOOK_DEBUG_MODE', 'false').lower() == 'true'
    BASE_URL = os.getenv('JELLYFIN_WEBHOOK_BASE_URL', '').rstrip('/')
    NON_VIDEO_FILE_FORMATS = ['jpg', 'metathumb', 'nfo', 'jpg', 'xml'] 
    TORRENTS_DATA_ROOT = os.getenv('TORRENTS_DATA_ROOT')

    # This is your "Source of Truth" in the code
    WEBHOOK_CONFIG = {
        "playback_stop": {
            "enabled": True,
            "name": "Jellyfin Watched Tagger",
            "description": "Tags a movie/series episode as `watched` in qBittorrent after it has been watched in Jellyfin.",
            "endpoint": "/playback_stop"
        }
    }

    @property
    def settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, 'r') as f:
                user_settings = json.load(f)
                # Merge user settings (enabled state) with the hardcoded config (descriptions/names)
                for key in self.WEBHOOK_CONFIG:
                    if key in user_settings:
                        self.WEBHOOK_CONFIG[key]['enabled'] = user_settings[key].get('enabled', True)
        return self.WEBHOOK_CONFIG

    def save_settings(self):
        # We only really need to save the 'enabled' state to keep the file small
        with open(self.SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

constants = Constants()