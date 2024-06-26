import React, { useState } from 'react';
import axios from 'axios';
import '../styles/searchbar.css';
import fallbackImage from '../images/fallback-cover.jpg'; // Adjust path based on your project structure

const SearchBar = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [hasTyped, setHasTyped] = useState(false); // New state for tracking typing

    const handleSearch = async (event) => {
        setQuery(event.target.value);
        setHasTyped(true); // Update hasTyped to true when typing starts
        if (event.target.value.length > 0) {
            try {
                const response = await axios.get(`/api/search?query=${event.target.value}`);
                console.log('API Response:', response.data);
                setResults(response.data);
            } catch (error) {
                console.error('Error fetching search results', error);
            }
        } else {
            setResults([]);
        }
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
                        {results.map((result, index) => (
                            <li key={result.id}>
                                <img 
                                    src={result.cover_art ? `data:image/jpeg;base64,${result.cover_art}` : fallbackImage} 
                                    alt="Cover Art" 
                                    width="50" 
                                    height="50"
                                />
                                <p>{index + 1}. <strong>{result.title}</strong> by <strong>{result.artist}</strong> from the album <strong>{result.album}</strong></p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    hasTyped && <p>No results found</p> // Show message if user has typed and no results found
                )}
            </div>
        </div>
    );
};

export default SearchBar;
