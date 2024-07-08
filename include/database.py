import os
import sqlite3
from mutagen import File
from mutagen.mp3 import HeaderNotFoundError
from datetime import datetime

def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_files (
            id INTEGER PRIMARY KEY,
            path TEXT,
            filename TEXT,
            title TEXT,
            album TEXT,
            artist TEXT,
            year INTEGER,
            duration REAL,
            bitrate INTEGER,
            genre TEXT,
            track_number INTEGER,
            disc_number INTEGER,
            composer TEXT,
            comment TEXT,
            cover_art BLOB,
            label TEXT,
            isrc TEXT,
            replaygain REAL,
            key TEXT,
            bpm INTEGER,
            last_modified INTEGER
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON audio_files(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_artist ON audio_files(artist)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_album ON audio_files(album)')
    conn.commit()
    return conn

def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def insert_metadata(cursor, metadata):
    cursor.execute('''
        INSERT INTO audio_files (path, filename, title, album, artist, year, duration, bitrate, genre, track_number, 
                                 disc_number, composer, comment, cover_art, label, isrc, replaygain, key, bpm, last_modified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metadata['path'], metadata['filename'], metadata['title'], metadata['album'], 
        metadata['artist'], metadata['year'], metadata['duration'], metadata['bitrate'], 
        metadata['genre'], metadata['track_number'], metadata['disc_number'], metadata['composer'],
        metadata['comment'], metadata['cover_art'], metadata['label'], metadata['isrc'], 
        metadata['replaygain'], metadata['key'], metadata['bpm'], metadata['last_modified']
    ))

def log_error(file_path, error_message):
    with open('error.log', 'a') as log_file:
        log_file.write(f"{datetime.now()} - {file_path}: {error_message}\n")

def get_metadata(file_path):
    try:
        audio = File(file_path)
        if audio is None:
            log_error(file_path, "Unsupported audio file or corrupted file")
            print(f"Fehler: {file_path} is not a supported audio file or damaged.")
            return None
        
        year_str = str(audio.tags.get('TDRC', 'Unknown').text[0]) if audio.tags and 'TDRC' in audio.tags else 'Unknown'
        
        try:
            year = int(datetime.strptime(year_str, '%Y-%m-%d').year)
        except ValueError:
            try:
                year = int(datetime.strptime(year_str, '%Y').year)
            except ValueError:
                year = 'Unknown'
        
        metadata = {
            'path': os.path.dirname(file_path),
            'filename': os.path.basename(file_path),
            'title': str(audio.tags.get('TIT2', 'Unknown')) if audio.tags else 'Unknown',
            'album': str(audio.tags.get('TALB', 'Unknown')) if audio.tags else 'Unknown',
            'artist': str(audio.tags.get('TPE1', 'Unknown')) if audio.tags else 'Unknown',
            'year': year,
            'duration': audio.info.length if audio.info else 0,
            'bitrate': audio.info.bitrate if audio.info else 0,
            'genre': str(audio.tags.get('TCON', 'Unknown')) if audio.tags else 'Unknown',
            'track_number': str(audio.tags.get('TRCK', 'Unknown')) if audio.tags else 'Unknown',
            'disc_number': str(audio.tags.get('TPOS', 'Unknown')) if audio.tags else 'Unknown',
            'composer': str(audio.tags.get('TCOM', 'Unknown')) if audio.tags else 'Unknown',
            'comment': str(audio.tags.get('COMM', 'Unknown')) if audio.tags else 'Unknown',
            'cover_art': audio.tags.get('APIC:', b'').data if audio.tags and 'APIC:' in audio.tags else None,
            'label': str(audio.tags.get('TPUB', 'Unknown')) if audio.tags else 'Unknown',
            'isrc': str(audio.tags.get('TSRC', 'Unknown')) if audio.tags else 'Unknown',
            'replaygain': str(audio.tags.get('RVA2', 'Unknown')) if audio.tags else 'Unknown',
            'key': str(audio.tags.get('TKEY', 'Unknown')) if audio.tags else 'Unknown',
            'bpm': str(audio.tags.get('TBPM', 'Unknown')) if audio.tags else 'Unknown',
            'last_modified': os.path.getmtime(file_path)
        }
        return metadata
    
    except HeaderNotFoundError:
        log_error(file_path, "can't sync to MPEG frame")
        print(f"Fehler: {file_path} can't be read as MPEG file.")
        return None

    except Exception as e:
        log_error(file_path, f"Unexpected error: {e}")
        print(f"Fehler: {file_path} can't be read. Error: {e}")
        return None

def get_existing_files(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT path, filename, last_modified FROM audio_files')
    return [{'path': row[0], 'filename': row[1], 'last_modified': row[2]} for row in cursor.fetchall()]

def process_files(directory, conn):
    cursor = conn.cursor()
    cursor.execute('BEGIN TRANSACTION')
    existing_files = {os.path.join(row['path'], row['filename']): row['last_modified'] for row in get_existing_files(conn)}
    file_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.ogg', '.flac', '.aac', '.ac3', '.adts', '.aiff', '.alac', '.amr', '.amr-wb', '.asf', '.au', '.avi', '.flac', '.gsm', '.id3v1', '.id3v2', '.ilbc', '.m4a', '.matroska', '.mpc', '.mp2', '.m4b', '.mka', '.mp3', '.ogg', '.opus', '.qt', '.riff', '.rtmp', '.sdp', '.shoutcast', '.vorbis', '.wav', '.wv', '.wma', '.wma-v1', '.wma-v2', '.wma-v2.5', '.wmv')):
                file_path = os.path.join(root, file)
                last_modified = os.path.getmtime(file_path)
                if file_path not in existing_files or existing_files[file_path] < last_modified:
                    metadata = get_metadata(file_path)
                    if metadata:
                        insert_metadata(cursor, metadata)
                        file_count += 1
    if file_count == 0:
        print("No new or updated audio files found. Proceed ...")
    cursor.execute('COMMIT')
    conn.commit()