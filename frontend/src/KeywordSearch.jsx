import React, { useState } from 'react';
import axios from 'axios';
import './KeywordSearch.css';
import { locationsList } from './data/locations';
import API_BASE_URL from './config';

function KeywordSearch() {

  const [formData, setFormData] = useState({
    brand_website: '',      
    competitor_website: '',
    location: '',
    seed_keywords: [],
    min_search_volume: 500,
    shopping_ads_budget: 0,
    search_ads_budget: 2000,
    pmax_ads_budget: 0
  });

  const [currentKeyword, setCurrentKeyword] = useState('');

  // Handle Enter key to add keyword
  const handleKeywordKeyDown = (e) => {
    if (e.key === 'Enter' && currentKeyword.trim()) {
      e.preventDefault();
      if (!formData.seed_keywords.includes(currentKeyword.trim())) {
        setFormData({
          ...formData,
          seed_keywords: [...formData.seed_keywords, currentKeyword.trim()]
        });
      }
      setCurrentKeyword('');
    }
  };

  // Remove keyword
  const removeKeyword = (indexToRemove) => {
    setFormData({
      ...formData,
      seed_keywords: formData.seed_keywords.filter((_, index) => index !== indexToRemove)
    });
  };

  
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/keywords/search`, formData);
      setResults(response.data);
    } catch (err) {
      setError('Failed to fetch keyword research. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="keyword-research-container">
      <h1> AI-Powered Keyword Search</h1>
      
      {/* Input Form */}

      <form onSubmit={handleSubmit} className="research-form">


        <div className="form-group">
          <label>Keywords (Optional):</label>
          
          {/* Display existing keywords */}
          {formData.seed_keywords.length > 0 && (
            <div className="keywords-display">
              {formData.seed_keywords.map((keyword, index) => (
                <span key={index} className="keyword-tag">
                  {keyword}
                  <span 
                    className="remove-keyword" 
                    onClick={() => removeKeyword(index)}
                  >
                    X
                  </span>
                </span>
              ))}
            </div>
          )}
          {/* Input for new keywords */}
          <input
            type="text"
            value={currentKeyword}
            onChange={(e) => setCurrentKeyword(e.target.value)}
            onKeyDown={handleKeywordKeyDown}
            placeholder="Type a keyword and press Enter"
            className="keyword-input"
          />
          <small className="helper-text">Press Enter to add each keyword</small>
        </div>



        <div className="form-group">
          <label>Website URL:</label>
          <input
            type="url"
            name="brand_website"
            value={formData.brand_website}
            onChange={handleInputChange}
            placeholder="https://...."
            required
          />
        </div>
        
        <div className="form-group">
          <label>Competitor URL (optional):</label>
          <input
            type="url"
            name="competitor_website"
            value={formData.competitor_website}
            onChange={handleInputChange}
            placeholder="https://...."
          />
        </div>

        <div className="form-group">
          <label>Service Location:</label>
          <select
            name="location"
            value={formData.location}
            onChange={handleInputChange} 
            required
            className="locations-dropdown"
          >
            <option value="" disabled>Select a city/region/country</option>
            {locationsList.map((location) => (
              <option key={location} value={location}>
                {location}
              </option>
            ))}
          </select>
        </div>

        {/* Minimum Search Volume */}
        <div className="form-group">
          <label>Minimum Monthly Searches for the Resulting Keywords:</label>
          <input
            type="number"
            name="min_search_volume"
            value={formData.min_search_volume}
            onChange={handleInputChange}
            min="0"
            placeholder="500"
            required
          />
          <small className="helper-text">Only show keywords with at least this many monthly searches</small>
        </div>



        <div className="form-group">
          <label>Search Ads Budget ($):</label>
          <input
            type="number"
            name="search_ads_budget"
            value={formData.search_ads_budget}
            onChange={handleInputChange}
            min="5"
            required
          />
        </div>

        <div className="form-group">
          <label>PMax Ads Budget ($):</label>
          <input
            type="number"
            name="pmax_ads_budget"
            value={formData.pmax_ads_budget}
            onChange={handleInputChange}
            min="5"
            required
          />
        </div>

        <div className="form-group">
          <label>Shopping Ads Budget ($):</label>
          <input
            type="number"
            name="shopping_ads_budget"
            value={formData.shopping_ads_budget}
            onChange={handleInputChange}
            min="5"
            required
          />
        </div>
        
        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Analyzing...' : 'Generate Keywords & Ad Groups'}
        </button>
      </form>

      {/* Error Display */}
      {error && (
        <div className="error-message">
           {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <p> AI is analyzing keywords and creating ad groups...</p>
          <p>This may take 20-30 seconds</p>
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="results-container">
          <div className="results-summary">
            <h2> Research Summary</h2>
            <div className="summary-stats">
              <div className="stat">
                <span className="stat-number">{results.total_keywords}</span>
                <span className="stat-label">Total Keywords</span>
              </div>
              <div className="stat">
                <span className="stat-number">{results.processing_time.toFixed(1)}s</span>
                <span className="stat-label">Processing Time</span>
              </div>
              <div className="stat">
                <span className="stat-number">{results.deliverable?.ad_groups?.length || 0}</span>
                <span className="stat-label">Ad Groups</span>
              </div>
            </div>
          </div>

          {/* Ad Groups Display */}
          {results.deliverable && (
            <div className="ad-groups-container">
              <h2> Recommended Ad Groups</h2>
              
              {results.deliverable.ad_groups.map((group, index) => (
                <div key={index} className="ad-group-card">
                  <div className="ad-group-header">
                    <h3>{group.group_name}</h3>
                    <div className="group-meta">
                      <span className="group-type">{group.group_type}</span>
                      <span className="budget">${group.budget_allocation}</span>
                      <span className="percentage">{group.budget_percentage}%</span> 
                    </div>
                  </div>
                  
                  <div className="keywords-list">
                    <h4>Keywords ({group.total_keywords}):</h4>
                    {group.keywords.map((keyword, keywordIndex) => (
                      <div key={keywordIndex} className="keyword-item">
                        <div className="keyword-main">
                          <span className="keyword-text">"{keyword.keyword}"</span>
                          <span className="search-volume">
                            {keyword.search_volume.toLocaleString()} searches/month
                          </span>
                        </div>
                        <div className="keyword-details">
                          <span className="competition">{keyword.competition_level}</span>
                          <span className="cpc-range">
                            ${keyword.cpc_low} - ${keyword.cpc_high} CPC
                          </span>
                          <span className="match-types">
                            {keyword.suggested_match_types.join(', ')}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default KeywordSearch;
