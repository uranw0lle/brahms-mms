// frontend/src/App.js

import React from 'react';
import './App.css';
import '@picocss/pico'
import SearchBar from './components/SearchBar';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Brahms Music Manager</h1>
                <SearchBar />
            </header>
        </div>
    );
}

export default App;
