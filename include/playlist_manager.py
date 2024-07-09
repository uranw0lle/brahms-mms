import os

def get_playlists(playlist_directory):
    playlists = [f for f in os.listdir(playlist_directory) if f.endswith('.m3u')]
    return playlists

def add_track_to_playlist(playlist_directory, playlist_name, file_path):
    playlist_path = os.path.join(playlist_directory, playlist_name)
    
    # Convert file_path to relative path with forward slashes
    rel_track_path = os.path.relpath(file_path, playlist_directory).replace(os.sep, '/')
    
    try:
        with open(playlist_path, 'a', encoding='utf-8') as playlist_file:
            playlist_file.write(f"{rel_track_path}\n")
        return True
    except Exception as e:
        print(f"Error adding track to playlist: {e}")
        return False