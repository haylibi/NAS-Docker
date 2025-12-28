# jellyfin_webhooks/api/logs/__init__.py
import re
import logging
from flask import Blueprint, jsonify, request
from jellyfin_webhooks.utils.constants import constants as c
from jellyfin_webhooks.utils.decorators import log_request

route = Blueprint('api_logs', __name__)

def parse_log_line(line):
    # Matches: [2023-10-27 10:00:00] INFO: Message here
    pattern = r'\[(.*?)\] (\w+): (.*)'
    match = re.match(pattern, line)
    if match:
        return {
            "time": match.group(1),
            "level": match.group(2),
            "msg": match.group(3)
        }
    return {"time": "Unknown", "level": "INFO", "msg": line}

@route.route(f'{c.BASE_URL}/api/logs')
@log_request(category="api", endpoint="logs")
def get_logs():
    page = request.args.get('page', 1, type=int)
    min_level_str = request.args.get('min_level', logging.getLevelName(logging.DEBUG)).upper()
    
    # Get numeric level from logging module
    min_level = logging.getLevelName(min_level_str)
    if not isinstance(min_level, int):
        min_level = logging.DEBUG

    per_page = 20
    
    all_logs = []
    try:
        with open(c.LOG_FILE, "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if line.strip():
                    log_entry = parse_log_line(line)
                    
                    # Convert log entry string level to int
                    entry_level_str = log_entry['level'].upper()
                    entry_level = logging.getLevelName(entry_level_str)
                    if not isinstance(entry_level, int):
                        entry_level = logging.INFO # Default if unknown
                        
                    if entry_level >= min_level:
                        all_logs.append(log_entry)
                        
    except FileNotFoundError:
        pass

    total_pages = max(1, (len(all_logs) + per_page - 1) // per_page)
    paginated = all_logs[(page-1)*per_page : page*per_page]
    total_items = len(all_logs)

    return jsonify({
        "data": paginated,
        "metadata": {"page": page, "total_pages": total_pages, "total_items": total_items}
    })