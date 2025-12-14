'use client';

/**
 * Location Autocomplete Component
 * Provides searchable dropdown for location selection
 */

import { useState, useEffect, useRef } from 'react';
import { MapPinIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import { searchLocations, LocationSuggestion } from '@/services/api';

interface LocationAutocompleteProps {
  value: string;
  onChange: (location: LocationSuggestion | null) => void;
  placeholder?: string;
  className?: string;
}

export default function LocationAutocomplete({
  value,
  onChange,
  placeholder = 'Search city...',
  className = '',
}: LocationAutocompleteProps) {
  const [query, setQuery] = useState(value);
  const [suggestions, setSuggestions] = useState<LocationSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<LocationSuggestion | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Search locations when query changes
  useEffect(() => {
    const searchLocationsAsync = async () => {
      if (query.length < 2) {
        setSuggestions([]);
        setIsOpen(false);
        return;
      }

      setLoading(true);
      try {
        const results = await searchLocations(query);
        setSuggestions(results);
        setIsOpen(results.length > 0);
      } catch (error) {
        // Silently handle errors
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(searchLocationsAsync, 300);
    return () => clearTimeout(debounceTimer);
  }, [query]);

  const handleSelect = (location: LocationSuggestion) => {
    setSelectedLocation(location);
    setQuery(location.displayName);
    setIsOpen(false);
    onChange(location);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    setSelectedLocation(null);
    
    if (newQuery.length < 2) {
      onChange(null);
    }
  };

  const handleInputFocus = () => {
    if (suggestions.length > 0 || query.length >= 2) {
      setIsOpen(true);
    }
  };

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      <div className="relative">
        <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-3 rounded-lg glass border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-900 dark:text-gray-100"
        />
        <ChevronDownIcon
          className={`absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 max-h-60 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              <div className="flex items-center justify-center">
                <svg className="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Searching worldwide...
              </div>
            </div>
          ) : suggestions.length === 0 ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              No locations found. Try a different search term.
            </div>
          ) : (
            <ul className="py-2">
              {suggestions.map((location, index) => (
                <li
                  key={`${location.city}-${location.country}-${index}`}
                  onClick={() => handleSelect(location)}
                  className="px-4 py-3 hover:bg-purple-50 dark:hover:bg-gray-700 cursor-pointer transition-colors border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-gray-100 flex items-center">
                        <MapPinIcon className="w-4 h-4 mr-2 text-purple-500" />
                        {location.displayName}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {location.latitude.toFixed(4)}°N, {location.longitude.toFixed(4)}°E
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

