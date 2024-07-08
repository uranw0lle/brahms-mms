import json
import os
import sqlite3
import base64
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from include.database import create_database, process_files
from include.searchfunction import search_database
from include.playlist_manager import (
    init_db, find_and_process_playlists, add_track_to_playlist, remove_track_from_playlist, get_db_connection
)

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

def load_config():
    config_file_path = 'config.json'
    default_config = {
        'music_directory': './Music',
        'playlist_directory': './Music/Playlists'
    }

    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            return json.load(config_file)
    else:
        with open(config_file_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)  # Add indent for pretty printing
        return default_config

def ensure_directories_exist(config):
    music_directory = config.get('music_directory', './Music').replace('\\', '/')
    playlist_directory = config.get('playlist_directory', f"{music_directory}/Playlists").replace('\\', '/')

    # Ensure the music directory exists
    if not os.path.exists(music_directory):
        os.makedirs(music_directory)
        print(f"Music directory created at {music_directory}")

    # Ensure the playlist directory exists
    if not os.path.exists(playlist_directory):
        os.makedirs(playlist_directory)
        print(f"Playlist directory created at {playlist_directory}")

    # Update config with playlist directory
    config['playlist_directory'] = playlist_directory
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)  # Add indent for pretty printing

    return music_directory, playlist_directory

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    conn = get_db_connection('audio_files.db')
    results = search_database(conn, [query])
    formatted_results = [
        {
            'id': row['id'],
            'title': row['title'],
            'artist': row['artist'],
            'album': row['album'],
            'cover_art': base64.b64encode(row['cover_art']).decode('utf-8') if row['cover_art'] else '',
        }
        for row in results
    ]
    conn.close()
    return jsonify(formatted_results)

@app.route('/api/audio_files', methods=['GET'])
def get_audio_files():
    conn = get_db_connection('audio_files.db')
    audio_files = conn.execute('SELECT * FROM audio_files').fetchall()
    conn.close()
    return jsonify([dict(row) for row in audio_files])

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    config = load_config()
    music_directory, playlist_directory = ensure_directories_exist(config)

    db_name = 'audio_files.db'
    conn = None

    if not os.path.exists(db_name):
        conn = create_database(db_name)
        print("No database found. Database created.")
    else:
        conn = get_db_connection(db_name)
        print("Database already exists. Proceed ...")

    init_db(conn)
    process_files(music_directory, conn)
    find_and_process_playlists(music_directory, conn)
    conn.close()

    app.run(debug=True)