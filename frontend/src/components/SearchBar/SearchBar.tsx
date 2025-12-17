import { useState, useEffect, useCallback, memo } from 'react'
import { searchApi } from '../../services/api'
import './SearchBar.css'

interface SearchBarProps {
  onSearch: (query: string) => void
}

const SearchBar = memo(({ onSearch }: SearchBarProps) => {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<any>(null)
  const [showSuggestions, setShowSuggestions] = useState(false)

  // Debounced search suggestions
  useEffect(() => {
    if (query.length >= 2) {
      const timeoutId = setTimeout(() => {
        searchApi.getSuggestions(query).then(setSuggestions)
        setShowSuggestions(true)
      }, 300) // 300ms debounce
      
      return () => clearTimeout(timeoutId)
    } else {
      setSuggestions(null)
      setShowSuggestions(false)
    }
  }, [query])

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()
    onSearch(query)
    setShowSuggestions(false)
  }, [query, onSearch])

  const handleSuggestionClick = useCallback((suggestion: string) => {
    setQuery(suggestion)
    onSearch(suggestion)
    setShowSuggestions(false)
  }, [onSearch])

  return (
    <div className="search-bar-container">
      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          className="search-input"
          placeholder="Search by text, tags, or categories..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length >= 2 && setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
        />
        <button type="submit" className="search-button">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        </button>
      </form>

      {showSuggestions && suggestions && (
        <div className="suggestions-dropdown">
          {suggestions.tags.length > 0 && (
            <div className="suggestion-section">
              <div className="suggestion-label">Tags</div>
              {suggestions.tags.map((tag: any) => (
                <div
                  key={tag.id}
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(tag.name)}
                >
                  {tag.name}
                </div>
              ))}
            </div>
          )}
          {suggestions.categories.length > 0 && (
            <div className="suggestion-section">
              <div className="suggestion-label">Categories</div>
              {suggestions.categories.map((cat: any) => (
                <div
                  key={cat.id}
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(cat.name)}
                >
                  {cat.name}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
})

SearchBar.displayName = 'SearchBar'

export default SearchBar

