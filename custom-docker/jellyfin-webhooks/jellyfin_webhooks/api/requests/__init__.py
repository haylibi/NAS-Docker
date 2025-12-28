import re
import os
import json
import math
from flask import Blueprint, request, jsonify, current_app
from jellyfin_webhooks.utils.constants import constants as c
from jellyfin_webhooks.utils.decorators import log_request

route = Blueprint('requests', __name__)

@route.route(f'{c.BASE_URL}/api/requests/endpoints', methods=['GET'])
@log_request(category="api", endpoint="requests/endpoints")
def get_endpoints_list():
    """
    Returns a list of all endpoints that have log files.
    """
    base_dir = "/app/data/requests"
    endpoints_map = {} # Key: "category/name" -> object
    
    if os.path.exists(base_dir):
        for category in os.listdir(base_dir):
            cat_path = os.path.join(base_dir, category)
            if not os.path.isdir(cat_path): continue
            
            for file in os.listdir(cat_path):
                if not file.endswith('.jsonl'): continue
                
                # Check for rotation pattern: name.timestamp.jsonl or name.jsonl
                match = re.match(r'^(.+?)(?:\.\d+)?\.jsonl$', file)
                if match:
                    name = match.group(1)
                    key = f"{category}/{name}"
                    if key not in endpoints_map:
                         endpoints_map[key] = {
                             "category": category,
                             "name": name,
                             "endpoint": name, # alias for compatibility
                             "id": f"{category}-{name}" # unique ID
                         }
    
    # Sort by category then name
    sorted_list = sorted(list(endpoints_map.values()), key=lambda x: (x['category'], x['name']))

    return jsonify({
        "data": sorted_list
    })

@route.route(f'{c.BASE_URL}/api/requests/<category>/<endpoint>', methods=['GET'])
@log_request(category="api", endpoint="requests/category/endpoint")
def get_request_logs(category, endpoint):
    """
    Get paginated logs for a specific category and endpoint.
    Query Params:
        page: int (default 1)
        per_page: int (default 50)
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    base_dir = f"/app/data/requests/{category}"
    filename = f"{endpoint}.jsonl"
    file_path = os.path.join(base_dir, filename)

    if not os.path.exists(file_path):
        return jsonify({
            "data": [],
            "metadata": {
                "page": page,
                "per_page": per_page,
                "total_items": 0,
                "total_pages": 0
            }
        })

    try:
        # Read all lines (efficient enough for 5000 lines)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse and reverse (newest first)
        logs = []
        for line in lines:
            if line.strip():
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        logs.reverse() # Newest first
        
        total_items = len(logs)
        total_pages = math.ceil(total_items / per_page)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_logs = logs[start_idx:end_idx]
        
        return jsonify({
            "data": paginated_logs,
            "metadata": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error reading request logs: {e}")
        return jsonify({"error": "Failed to read logs"}), 500
