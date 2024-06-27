import os
import glob
import sqlite3
from datetime import datetime

def init_db(conn):
    cursor = conn.cursor()
    
    # Erstellen der Playlists Tabelle
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        created_at DATETIME
    )
    ''')
    
    # Erstellen der Playlist-Items Tabelle
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER,
        track_path TEXT,
        track_title TEXT,
        track_duration INTEGER,
        position INTEGER,
        FOREIGN KEY (playlist_id) REFERENCES playlists (id)
    )
    ''')
    
    conn.commit()

def read_m3u_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    tracks = []
    track_info = {}
    position = 0

    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            info = line[8:].split(',', 1)
            track_info['duration'] = int(info[0])
            track_info['title'] = info[1] if len(info) > 1 else ''
        elif not line.startswith('#'):
            track_info['path'] = line
            track_info['position'] = position
            tracks.append(track_info)
            track_info = {}
            position += 1

    return tracks

def find_and_process_playlists(music_directory, conn):
    m3u_files = glob.glob(os.path.join(music_directory, '**/*.m3u'), recursive=True)
    m3u8_files = glob.glob(os.path.join(music_directory, '**/*.m3u8'), recursive=True)
    playlist_files = m3u_files + m3u8_files
    
    for file_path in playlist_files:
        playlist_name = os.path.basename(file_path)
        
        # Prüfen, ob die Playlist bereits in der DB existiert
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM playlists WHERE name = ?', (playlist_name,))
        playlist = cursor.fetchone()
        
        if playlist:
            playlist_id = playlist['id']
            cursor.execute('DELETE FROM playlist_items WHERE playlist_id = ?', (playlist_id,))
        else:
            cursor.execute('INSERT INTO playlists (name, created_at) VALUES (?, ?)', (playlist_name, datetime.now()))
            playlist_id = cursor.lastrowid
        
        tracks = read_m3u_file(file_path)
        
        for track in tracks:
            cursor.execute('''
                INSERT INTO playlist_items (playlist_id, track_path, track_title, track_duration, position)
                VALUES (?, ?, ?, ?, ?)
            ''', (playlist_id, track['path'], track.get('title', ''), track.get('duration', 0), track['position']))
        
        conn.commit()

def update_playlist_file(playlist_id, music_directory, conn):
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM playlists WHERE id = ?', (playlist_id,))
    playlist_name = cursor.fetchone()['name']
    
    cursor.execute('SELECT * FROM playlist_items WHERE playlist_id = ? ORDER BY position', (playlist_id,))
    tracks = cursor.fetchall()
    
    file_path = os.path.join(music_directory, playlist_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')
        for track in tracks:
            if track['track_duration'] > 0:
                file.write(f'#EXTINF:{track["track_duration"]},{track["track_title"]}\n')
            file.write(f'{track["track_path"]}\n')

def add_track_to_playlist(playlist_id, track_path, conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(position) FROM playlist_items WHERE playlist_id = ?', (playlist_id,))
    max_position = cursor.fetchone()[0] or 0
    new_position = max_position + 1
    
    cursor.execute('''
        INSERT INTO playlist_items (playlist_id, track_path, position)
        VALUES (?, ?, ?)
    ''', (playlist_id, track_path, new_position))
    conn.commit()
    
    # Update the playlist file on disk
    cursor.execute('SELECT name FROM playlists WHERE id = ?', (playlist_id,))
    playlist_name = cursor.fetchone()['name']
    update_playlist_file(playlist_id, music_directory, conn)

def remove_track_from_playlist(playlist_id, track_id, conn):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM playlist_items WHERE id = ?', (track_id,))
    conn.commit()
    
    # Update the playlist file on disk
    cursor.execute('SELECT name FROM playlists WHERE id = ?', (playlist_id,))
    playlist_name = cursor.fetchone()['name']
    update_playlist_file(playlist_id, music_directory, conn)

# Ensure the DB connection uses Row factory
def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn