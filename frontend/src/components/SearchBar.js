import React, { useState } from 'react';
import axios from 'axios';
import '../styles/searchbar.css';
import fallbackImage from '../images/fallback-cover.jpg'; // Adjust path based on your project structure

const SearchBar = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);

    const handleSearch = async (event) => {
        setQuery(event.target.value);
        if (event.target.value.length > 2) {  // Trigger search on input length > 2. It might make sense to check if that has an impact performance wise
            try {
                const response = await axios.get(`/api/search?query=${event.target.value}`);
                setResults(response.data);
            } catch (error) {
                console.error('Error fetching search results', error);
            }
        } else {
            setResults([]);
        }
    };

    return (
        <div>
            <input 
                type="text" 
                className='search-bar'
                value={query} 
                onChange={handleSearch} 
                placeholder="Title, Artist, or Album..." 
            />
            <div>
                {results.length > 0 && (
                    <ul>
                        {results.map((result, index) => (
                            <li key={result.id}>
                                <img 
                                    src={result.cover_art ? `data:image/jpeg;base64,${result.cover_art}` : fallbackImage} 
                                    alt="Cover Art" 
                                    width="50" 
                                    height="50"
                                />
                                <p>{index + 1}. {result.title} by {result.artist} from the album {result.album}</p>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default SearchBar;
