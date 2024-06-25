from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sqlite3
from include.database import create_database, process_files
from include.searchfunction import search_database

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('audio_files.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    conn = get_db_connection()
    results = search_database(conn, [query])  # Pass query as a list
    formatted_results = [
        {
            'id': row['id'],
            'title': row['title'],
            'artist': row['artist'],
            'album': row['album'],
            'cover_art': row['cover_art'].decode('utf-8') if row['cover_art'] else '',
        }
        for row in results
    ]
    conn.close()
    return jsonify(formatted_results)

@app.route('/api/audio_files', methods=['GET'])
def get_audio_files():
    conn = get_db_connection()
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
    db_name = 'audio_files.db'
    music_directory = os.getcwd()

    if not os.path.exists(db_name):
        conn = create_database(db_name)
        print("Database created.")
    else:
        conn = sqlite3.connect(db_name)
        print("Database already exists.")

    process_files(music_directory, conn)
    conn.close()

    app.run(debug=True)
