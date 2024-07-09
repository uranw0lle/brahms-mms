import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import '../styles/searchbar.css';
import fallbackImage from '../images/fallback-cover.jpg';
import addToPlaylistIcon from '../images/icons/add-to-playlist-icon.svg';
import { debounce } from 'lodash';

const SearchBar = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [hasTyped, setHasTyped] = useState(false);
    const [playlists, setPlaylists] = useState([]);
    const [selectedTrack, setSelectedTrack] = useState(null);
    const [addedTrackId, setAddedTrackId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);

    useEffect(() => {
        fetchPlaylists();
    }, []);

    const fetchPlaylists = async () => {
        try {
            const response = await axios.get('/api/playlists');
            setPlaylists(response.data);
        } catch (error) {
            console.error('Error fetching playlists', error);
        }
    };

    const fetchResults = useCallback(async (searchQuery, page) => {
        if (!searchQuery) {
            setResults([]);
            return;
        }
        setLoading(true);
        setHasTyped(true);
        try {
            const response = await axios.get(`/api/search?query=${searchQuery}&page=${page}`);
            if (page === 1) {
                setResults(response.data);
            } else {
                setResults(prevResults => [...prevResults, ...response.data]);
            }
        } catch (error) {
            console.error('Error fetching search results', error);
        } finally {
            setLoading(false);
        }
    }, []);

    const debouncedFetch = useCallback(
        debounce((newQuery) => {
            setCurrentPage(1);
            fetchResults(newQuery, 1);
        }, 300),
        [fetchResults]
    );

    const handleSearch = (event) => {
        const newQuery = event.target.value;
        setQuery(newQuery);
        debouncedFetch(newQuery);
    };

    const handleLoadMore = () => {
        const newPage = currentPage + 1;
        setCurrentPage(newPage);
        fetchResults(query, newPage);
    };

    const handleAddToPlaylist = (track) => {
        setSelectedTrack(track);
    };

    const addToPlaylist = async (playlistName) => {
        try {
            await axios.post('/api/add_to_playlist', {
                trackId: selectedTrack.id,
                playlist: playlistName
            });
            setAddedTrackId(selectedTrack.id);
            setTimeout(() => setAddedTrackId(null), 2000); // Reset after 2 seconds
        } catch (error) {
            console.error('Error adding track to playlist', error);
        }
        setSelectedTrack(null);
    };

    return (
        <div className='container-fluid'>
            <input 
                type="text" 
                className='search-bar'
                value={query} 
                onChange={handleSearch} 
                placeholder="Title, Artist, or Album..." 
            />
            <div>
                {results.length > 0 ? (
                    <ul>
                        {results.map((result) => (
                            <li key={result.id} className={addedTrackId === result.id ? 'added-to-playlist' : ''}>
                                <img 
                                    src={result.cover_art ? `data:image/jpeg;base64,${result.cover_art}` : fallbackImage} 
                                    alt="Cover Art" 
                                />
                                <p>
                                    <strong>{result.title}</strong><br />
                                    <i>{result.artist}</i><br />
                                    <strong>{result.album}</strong>
                                </p>
                                <img 
                                    src={addToPlaylistIcon} 
                                    alt="Add to Playlist" 
                                    onClick={() => handleAddToPlaylist(result)}
                                    style={{ cursor: 'pointer', width: '24px', height: '24px' }}
                                />
                            </li>
                        ))}
                    </ul>
                ) : (
                    hasTyped && !loading && <p>No results found</p>
                )}
                {results.length > 0 && !loading && (
                    <button 
                    className='outline'
                    onClick={handleLoadMore}>Load More</button>
                )}
                {loading && <p>Loading...</p>}
            </div>
            {selectedTrack && (
                <div className="modal">
                    <h3>Add "{selectedTrack.title}" to playlist:</h3>
                    <ul>
                        {playlists.map((playlist) => (
                            <li key={playlist} onClick={() => addToPlaylist(playlist)}>
                                {playlist}
                            </li>
                        ))}
                    </ul>
                    <button 
                    className='outline'
                    onClick={() => setSelectedTrack(null)}>Cancel</button>
                </div>
            )}
        </div>
    );
};

export default SearchBar;