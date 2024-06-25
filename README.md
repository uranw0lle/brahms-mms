# Brahms-MMS

Brahms-MMS is a tool designed to efficiently manage large music collections locally. It scans specified folders and their subfolders for audio files, extracting metadata from ID3 tags to populate a local database. While currently focused on managing music metadata and offering a robust search functionality, future plans include expanding its capabilities to manage playlists, favorite songs, albums, and artists.

## Technologies Used

### Frontend

- **React**: JavaScript library for building user interfaces.

### Backend

- **Mutagen**: Reading meta information from audio files.
- **Flask**: Lightweight Python web framework.
- **Python**: Programming language used for backend development.
- **SQLite**: Embedded relational database management system.

## Features

- **Local Database Creation**: Automatically generates a local database using ID3 tag information from scanned audio files. [Done]
- **Efficient Search Functionality**: Provides fast and effective search capabilities across music metadata. [Done]
- **Playlist Management**: Planned feature for managing '.m3u' and '.m3u8' playlists. [TODO]
- **Favorite Songs Management**: Future functionality to mark and organize favorite songs. [TODO]
- **Favorite Albums Management**: Planned feature to manage and categorize favorite albums. [TODO]
- **Favorite Artists Management**: Future capability for organizing favorite artists. [TODO]

## Stretch Goals

- **Remote Folder Support**: Integration to access and manage music stored in remote folders such as SMB shares. [TODO]
- **Remote Database Integration**: Capability to connect and synchronize with remote databases. [TODO]
- **External APIs Integration**: Integration with LastFM and MusicBrainz for enhanced metadata and music information retrieval.[TODO]
