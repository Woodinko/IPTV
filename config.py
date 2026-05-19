"""
Configuration file for M3U Playlist Server
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Playlist directory
PLAYLIST_DIR = os.getenv('PLAYLIST_DIR', str(BASE_DIR / 'playlists'))

# Flask configuration
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', 5000))

# Upload configuration
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
ALLOWED_EXTENSIONS = {'m3u', 'm3u8'}
