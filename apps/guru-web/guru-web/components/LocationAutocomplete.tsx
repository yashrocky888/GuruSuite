'use client';

/**
 * Location Autocomplete Component
 * Provides searchable dropdown for location selection
 * Fixed for production-grade UX
 */

import { useState, useEffect, useRef } from 'react';
import { MapPinIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import { searchLocation, LocationSuggestion, getTimezoneFromCoordinates, handleError } from '@/services/api';

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
  const [query, setQuery] = useState(value || "");
  const [results, setResults] = useState<Array<{ label: string; lat: number; lon: number; display_name?: string; name?: string; country?: string; state?: string }>>([]);
  const [selectedLocation, setSelectedLocation] = useState<LocationSuggestion | null>(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isSelectingLocation, setIsSelectingLocation] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync with external value prop
  useEffect(() => {
    if (value !== query) {
      setQuery(value || "");
    }
  }, [value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Search locations when query changes (with debounce and selection guard)
  useEffect(() => {
    // Ignore API updates while user is selecting a location
    if (isSelectingLocation) {
      return;
    }

    if (query.length < 3) {
      setResults([]);
      setOpen(false);
      return;
    }

    const fetch = async () => {
      // Double-check: still not selecting
      if (isSelectingLocation) {
        return;
      }

      setLoading(true);
      try {
        const data = await searchLocation(query);
        
        // Triple-check: user might have clicked while we were fetching
        if (!isSelectingLocation) {
          setResults(data);
          setOpen(data.length > 0);
        }
      } catch (error: any) {
        // CRITICAL: Properly classify error (Axios vs runtime)
        // searchLocation uses axios, so this is likely an Axios error
        // But we classify it properly to prevent {} errors
        handleError(error, "LocationAutocomplete.fetch");
        // Silently fail for UX (errors already logged by handleError)
        if (!isSelectingLocation) {
          setResults([]);
          setOpen(false);
        }
      } finally {
        if (!isSelectingLocation) {
          setLoading(false);
        }
      }
    };

    const debounceTimer = setTimeout(fetch, 300);
    return () => clearTimeout(debounceTimer);
  }, [query, isSelectingLocation]);

  const handleSelect = async (item: { label: string; lat: number; lon: number; display_name?: string; name?: string; country?: string; state?: string }) => {
    // Immediately set selecting flag to prevent API overwrites
    setIsSelectingLocation(true);
    
    // Immediately update UI (no waiting for async operations)
    setQuery(item.label);
    setResults([]);
    setOpen(false);
    setLoading(false);
    
    // Immediately notify parent with basic data (lat/lon available now)
    const immediateLocation: LocationSuggestion = {
      city: item.name || item.label.split(',')[0] || '',
      country: item.country || item.label.split(',').pop()?.trim() || 'Unknown',
      latitude: item.lat,
      longitude: item.lon,
      timezone: '', // Will be updated below
      displayName: item.display_name || item.label,
    };
    
    // Notify parent immediately with available data
    onChange(immediateLocation);
    
    // Get timezone asynchronously (non-blocking)
    try {
      const timezone = await getTimezoneFromCoordinates(item.lat, item.lon);
      
      // Create full LocationSuggestion object with timezone
      const fullLocation: LocationSuggestion = {
        ...immediateLocation,
        timezone: timezone,
      };
      
      // Store selection and notify parent again with complete data
      setSelectedLocation(fullLocation);
      onChange(fullLocation);
    } catch (error: any) {
      // If timezone fetch fails, keep the immediate location (already set)
      handleError(error, "LocationAutocomplete.handleSelect.timezone");
      setSelectedLocation(immediateLocation);
    } finally {
      // Re-enable API updates after selection is complete
      setIsSelectingLocation(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    setSelectedLocation(null);
    setIsSelectingLocation(false); // Reset selection flag on new input
    
    if (newQuery.length < 3) {
      onChange(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Pressing Enter auto-selects first suggestion
    if (e.key === 'Enter' && results.length > 0 && !isSelectingLocation) {
      e.preventDefault();
      handleSelect(results[0]);
    }
  };

  const handleInputFocus = () => {
    if (results.length > 0 || query.length >= 3) {
      setOpen(true);
    }
  };

  return (
    <div ref={wrapperRef} className={`relative ${className}`} style={{ overflow: 'visible' }}>
      <div className="relative">
        <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 z-10" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-3 rounded-lg glass border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-900 dark:text-gray-100"
        />
        <ChevronDownIcon
          className={`absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 transition-transform z-10 ${
            open ? 'rotate-180' : ''
          }`}
        />
      </div>

      {/* Dropdown - Fixed z-index and positioning */}
      {open && (
        <div 
          className="absolute z-50 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-auto"
          style={{ position: 'absolute', zIndex: 50 }}
        >
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
          ) : results.length === 0 ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              No locations found. Try a different search term.
            </div>
          ) : (
            <ul className="py-2">
              {results.map((item, idx) => (
                <li
                  key={idx}
                  className="px-4 py-3 cursor-pointer hover:bg-purple-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                  onClick={() => handleSelect(item)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-gray-100 flex items-center">
                        <MapPinIcon className="w-4 h-4 mr-2 text-purple-500" />
                        {item.label}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {item.lat.toFixed(4)}°N, {item.lon.toFixed(4)}°E
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
