import os

QBT_HOST = os.getenv('QBT_HOST', 'http://gluetun:8080')
QBT_USER = os.getenv('QBT_USER', 'admin')
QBT_PASS = os.getenv('QBT_PASS', 'adminadmin')

PORT = int(os.getenv('PORT', 5000))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()