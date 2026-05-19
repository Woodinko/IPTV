#!/usr/bin/env python3
"""
M3U Playlist Server
Simple Flask application for serving M3U playlists
"""

from flask import Flask, render_template, send_file, jsonify, request
from pathlib import Path
import os

app = Flask(__name__)

# Configuration
PLAYLIST_DIR = Path(__file__).parent / 'playlists'
PLAYLIST_DIR.mkdir(exist_ok=True)


@app.route('/')
def home():
    """Home page - list all available endpoints"""
    return jsonify({
        'message': 'M3U Playlist Server',
        'version': '1.0.0',
        'endpoints': {
            'playlists': '/playlists',
            'get_playlist': '/playlist/<filename>',
            'upload': '/upload'
        }
    })


@app.route('/playlists')
def list_playlists():
    """List all available playlist files"""
    playlists = []
    
    if PLAYLIST_DIR.exists():
        for file in PLAYLIST_DIR.glob('*.m3u'):
            playlists.append({
                'filename': file.name,
                'size': file.stat().st_size,
                'url': f'/playlist/{file.name}'
            })
    
    return jsonify({
        'count': len(playlists),
        'playlists': playlists
    })


@app.route('/playlist/<filename>')
def serve_playlist(filename):
    """Serve a specific playlist file"""
    # Validate filename to prevent directory traversal
    if '..' in filename or '/' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    file_path = PLAYLIST_DIR / filename
    
    # Check if file exists and is an M3U file
    if not file_path.exists():
        return jsonify({'error': 'Playlist not found'}), 404
    
    if not filename.lower().endswith('.m3u'):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        return send_file(
            file_path,
            mimetype='audio/mpegurl',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_playlist():
    """Upload a new playlist file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.m3u'):
        return jsonify({'error': 'Only .m3u files are allowed'}), 400
    
    try:
        file.save(PLAYLIST_DIR / file.filename)
        return jsonify({
            'message': 'Playlist uploaded successfully',
            'filename': file.filename,
            'url': f'/playlist/{file.filename}'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/playlist/<filename>/info')
def playlist_info(filename):
    """Get information about a playlist"""
    if '..' in filename or '/' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    file_path = PLAYLIST_DIR / filename
    
    if not file_path.exists():
        return jsonify({'error': 'Playlist not found'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
            # Count channels
            channel_count = sum(1 for line in lines if line.startswith('#EXTINF'))
            
            return jsonify({
                'filename': filename,
                'size': file_path.stat().st_size,
                'channels': channel_count,
                'lines': len(lines)
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
