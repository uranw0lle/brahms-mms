// frontend/src/App.js

import React from 'react';
import './App.css';
import SearchBar from './components/SearchBar';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Music Search App</h1>
                <SearchBar />
            </header>
        </div>
    );
}

export default App;
