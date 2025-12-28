
import os
import json
import logging
import time
from threading import Lock

class RequestLogger:
    _locks = {}
    _lock_access = Lock()

    @classmethod
    def get_lock(cls, key):
        """Get a named lock for a specific file path to ensure thread safety."""
        with cls._lock_access:
            if key not in cls._locks:
                cls._locks[key] = Lock()
            return cls._locks[key]

    @staticmethod
    def write_log(category: str, endpoint: str, data: dict):
        """
        Writes a log entry to /app/data/requests/<category>/<endpoint>.jsonl
        Rotates file if it exceeds 5000 lines.
        """
        # 1. Determine paths
        base_dir = f"/app/data/requests/{category}"
        os.makedirs(base_dir, exist_ok=True)
        
        filename = f"{endpoint}.jsonl"
        file_path = os.path.join(base_dir, filename)
        
        lock = RequestLogger.get_lock(file_path)
        
        with lock:
            request_log_limit = 5000
            
            # 2. Check rotation (Line counting)
            # Optimization: Check size first? 5000 lines * ~1KB = 5MB. 
            # If file doesn't exist, lines = 0.
            if os.path.exists(file_path):
                try:
                    # Counting lines efficiently
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)
                    
                    if line_count >= request_log_limit:
                        # Rotate
                        timestamp = int(time.time())
                        rotated_name = f"{endpoint}.{timestamp}.jsonl"
                        rotated_path = os.path.join(base_dir, rotated_name)
                        os.rename(file_path, rotated_path)
                        logging.info(f"Rotated log file {file_path} to {rotated_path}")
                except Exception as e:
                    logging.error(f"Error checking/rotating log file {file_path}: {e}")

            # 3. Write data
            try:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data) + "\n")
            except Exception as e:
                logging.error(f"Failed to write request log to {file_path}: {e}")
