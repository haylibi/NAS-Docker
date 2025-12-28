
import functools
import time
import json
from flask import request, g
from jellyfin_webhooks.utils.request_logger import RequestLogger

def log_request(category="default", endpoint=None):
    """
    Decorator to log request and response details to a JSONL file.
    
    :param category: The category folder for the log (e.g., 'webhook', 'api').
    :param endpoint: The specific endpoint name for the log file (e.g., 'add_watched_tag').
                     If None, it tries to use the decorated function's name.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Determine endpoint name if not provided
            endpoint_name = endpoint
            if not endpoint_name:
                endpoint_name = func.__name__

            endpoint_name = endpoint_name.format(**kwargs).replace('/', '_')

            # Capture request items
            start_time = time.time()
            
            # Helper to get body safely
            req_body = {}
            try:
                if request.is_json:
                    req_body = request.get_json(silent=True) or {}
                else:
                    req_body = {"text": request.get_data(as_text=True)}
            except Exception:
                req_body = {"error": "Could not parse body"}

            headers = dict(request.headers)
            headers.pop('Cookie', None) # Cookie may contain sensitive data

            # Redact sensitive headers if needed (optional, simplistic for now)
            if 'Authorization' in headers:
                headers['Authorization'] = 'REDACTED'

            # Execute the function
            try:
                response = func(*args, **kwargs)
            except Exception as e:
                # Log exception and re-raise
                duration_ms = int((time.time() - start_time) * 1000)
                _log_entry(category, endpoint_name, start_time, duration_ms, headers, req_body, 500, {"error": str(e)})
                raise e

            # Process response
            duration_ms = int((time.time() - start_time) * 1000)
            
            status_code = 200
            resp_body = {}

            # Flask response objects can be complicated.
            # If it's a tuple (body, status), unpack it.
            # If it's a Response object, extract data.
            try:
                if isinstance(response, tuple):
                    if len(response) >= 2:
                        status_code = response[1]
                        resp_body = _parse_response_body(response[0])
                    else:
                        resp_body = _parse_response_body(response[0])
                # Check if it's a Flask Response object
                elif hasattr(response, 'status_code'):
                    status_code = response.status_code
                    if response.is_json:
                         resp_body = response.get_json(silent=True)
                    else:
                        # Be careful with large bodies, maybe truncate?
                        resp_body = {"text": response.get_data(as_text=True)}
                else:
                    # Just a body returned
                    resp_body = _parse_response_body(response)
            except Exception:
                resp_body = {"error": "Could not parse response"}

            _log_entry(category, endpoint_name, start_time, duration_ms, headers, req_body, status_code, resp_body)

            return response
        return wrapper
    return decorator

def _parse_response_body(body):
    if isinstance(body, dict) or isinstance(body, list):
        return body
    try:
        # Try to see if it's a JSON string
        return body.json
    except:
        return str(body)

def _log_entry(category, endpoint, start_time, duration, headers, req_body, status, resp_body):
    entry = {
        "timestamp": start_time,
        "date_iso": time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(start_time)),
        "method": request.method,
        "url": request.url,
        "remote_addr": request.remote_addr,
        "headers": headers,
        "body": req_body,
        "duration_ms": duration,
        "response": {
            "status": status,
            "body": resp_body
        }
    }
    RequestLogger.write_log(category, endpoint, entry)
