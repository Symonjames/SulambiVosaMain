import React, { useState, useEffect, useRef } from 'react';
import {
  TextField,
  InputAdornment,
  IconButton,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemAvatar,
  Avatar,
} from '@mui/material';
import {
  Search,
  Clear,
  CalendarToday,
  LocationOn,
} from '@mui/icons-material';
import FlexBox from '../FlexBox';
import { getAllEvents } from '../../api/events';
import { ExternalEventProposalType, InternalEventProposalType } from '../../interface/types';

interface ProjectSearchBarProps {
  onSearchResults: (results: (ExternalEventProposalType | InternalEventProposalType)[]) => void;
  onYearFilter: (year: string) => void;
  placeholder?: string;
  showFilters?: boolean;
  maxWidth?: string;
  leftSlot?: React.ReactNode;
}

const ProjectSearchBar: React.FC<ProjectSearchBarProps> = ({
  onSearchResults,
  onYearFilter,
  placeholder = "Search projects by title, location, or description...",
  showFilters = true,
  maxWidth = "600px",
  leftSlot
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [allEvents, setAllEvents] = useState<(ExternalEventProposalType | InternalEventProposalType)[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<(ExternalEventProposalType | InternalEventProposalType)[]>([]);
  const [selectedYear, setSelectedYear] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestionsVisible, setSuggestionsVisible] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Debounced search to prevent excessive re-renders
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 150); // 150ms debounce
    
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Load events once
  useEffect(() => {
    getAllEvents()
      .then((response) => {
        const externalEvents: ExternalEventProposalType[] = response.data?.external || [];
        const internalEvents: InternalEventProposalType[] = response.data?.internal || [];
        const all = [...externalEvents, ...internalEvents];
        setAllEvents(all);
        setFilteredEvents(all);
        onSearchResults(all);
      })
      .catch((error) => {
        console.error('Error fetching events:', error);
        setAllEvents([]);
        setFilteredEvents([]);
        onSearchResults([]);
      });
  }, [onSearchResults]);

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('recentProjectSearches');
    if (saved) setRecentSearches(JSON.parse(saved));
  }, []);

  // Persist recent searches helper
  const addToRecentSearches = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed) return;
    setRecentSearches(prev => {
      const updated = [trimmed, ...prev.filter(s => s !== trimmed)].slice(0, 5);
      localStorage.setItem('recentProjectSearches', JSON.stringify(updated));
      return updated;
    });
  };

  // Filtering logic (applies search term and filters) - Uses debounced search term
  useEffect(() => {
    let filtered = allEvents.slice();

    if (debouncedSearchTerm.trim()) {
      const term = debouncedSearchTerm.toLowerCase();
      filtered = filtered.filter(event =>
        (event.title || '').toLowerCase().includes(term) ||
        ((event as ExternalEventProposalType).location || '').toLowerCase().includes(term) ||
        ((event as InternalEventProposalType).venue || '').toLowerCase().includes(term) ||
        ((event.description || '')).toLowerCase().includes(term) ||
        ((event as any).objectives || '').toLowerCase().includes(term) ||
        ((event as ExternalEventProposalType).beneficiaries || '').toLowerCase().includes(term)
      );
    }

    if (selectedYear !== 'all') {
      filtered = filtered.filter(event => {
        const start = event.durationStart ? new Date(event.durationStart) : null;
        const year = start ? start.getFullYear().toString() : '';
        return year === selectedYear;
      });
    }

    if (selectedStatus !== 'all') {
      filtered = filtered.filter(event => (event as any).status === selectedStatus);
    }

    if (selectedType !== 'all') {
      if (selectedType === 'external') filtered = filtered.filter(evt => 'location' in evt);
      if (selectedType === 'internal') filtered = filtered.filter(evt => 'venue' in evt);
    }

    setFilteredEvents(filtered);
    // Only emit results automatically if user typed something or changed filters
    onSearchResults(filtered);
  }, [debouncedSearchTerm, selectedYear, selectedStatus, selectedType, allEvents, onSearchResults]);

  // Suggestions: return up to 5 matching event objects for predictive UI - Memoized to prevent unnecessary recalculations
  const suggestionEvents = React.useMemo(() => {
    if (!searchTerm.trim()) return [];
    const term = searchTerm.toLowerCase();
    const matches = allEvents.filter(event =>
      (event.title || '').toLowerCase().includes(term) ||
      ((event as ExternalEventProposalType).location || '').toLowerCase().includes(term) ||
      ((event as InternalEventProposalType).venue || '').toLowerCase().includes(term)
    );
    return matches.slice(0, 5);
  }, [searchTerm, allEvents]);

  const handleSuggestionClick = (evt: ExternalEventProposalType | InternalEventProposalType) => {
    const title = evt.title || '';
    setSearchTerm(title);
    setShowSuggestions(false);
    addToRecentSearches(title);
    setFilteredEvents([evt]);
    onSearchResults([evt]);
  };

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    // Show suggestions when typing or when focusing and empty input
    setShowSuggestions(true);
    // Delay visibility for smooth transition
    setTimeout(() => setSuggestionsVisible(true), 10);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setShowSuggestions(false);
    setSuggestionsVisible(false);
    setFilteredEvents(allEvents);
    onSearchResults(allEvents);
  };

  // Click outside to close suggestion dropdown
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (!wrapperRef.current) return;
      if (!wrapperRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
        setSuggestionsVisible(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard: Enter = perform search (use filteredEvents), Escape = close
  const handleKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === 'Enter') {
      setShowSuggestions(false);
      setSuggestionsVisible(false);
      addToRecentSearches(searchTerm);
      onSearchResults(filteredEvents);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setSuggestionsVisible(false);
    }
  };

  const handleFocus = () => {
    setShowSuggestions(true);
    setTimeout(() => setSuggestionsVisible(true), 10);
  };

  // Util: format date range nicely
  const formatDateRange = (start?: string | Date | number, end?: string | Date | number) => {
    if (!start) return '';
    const s = new Date(start);
    const e = end ? new Date(end) : null;
    const sStr = s.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    if (!e) return sStr;
    const eStr = e.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    return `${sStr} — ${eStr}`;
  };

  // Helper to get location/venue text
  const getLocationLabel = (evt: any) => {
    if ('location' in evt && evt.location) return evt.location;
    if ('venue' in evt && evt.venue) return evt.venue;
    return '';
  };

  const availableYears = React.useMemo(() => {
    const years = new Set<string>();
    allEvents.forEach(event => {
      if (event.durationStart) {
        const y = new Date(event.durationStart).getFullYear().toString();
        years.add(y);
      }
    });
    return Array.from(years).sort((a, b) => b.localeCompare(a));
  }, [allEvents]);

  return (
    <Box sx={{ width: '100%', maxWidth, position: 'relative' }} ref={wrapperRef}>
      <FlexBox
        alignItems="center"
        justifyContent="space-between"
        gap={2}
        mb={0}
        sx={{
          flexWrap: { xs: 'wrap', md: 'nowrap' },
          width: '100%',
          '& > *': { flexShrink: 0 }
        }}
      >
        <FlexBox
          alignItems="center"
          gap={2}
          sx={{
            flex: { xs: '1 1 100%', md: '1 1 auto' },
            minWidth: 0,
            flexWrap: { xs: 'wrap', md: 'nowrap' }
          }}
        >
          {leftSlot && (<Box sx={{ flex: '0 0 auto' }}>{leftSlot}</Box>)}

          {/* IMPORTANT: this wrapper is relative - dropdown anchored to this width */}
          <Box
            sx={{
              position: "relative",
              width: '100%',
              flex: { xs: '1 1 100%', md: '1 1 640px' },
              maxWidth: { xs: '100%', md: 640 },
              minWidth: 280
            }}
          >
            <TextField
              fullWidth
              inputRef={inputRef}
              placeholder={placeholder}
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              onFocus={handleFocus}
              onKeyDown={handleKeyDown}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search color="action" />
                  </InputAdornment>
                ),
                endAdornment: searchTerm && (
                  <InputAdornment position="end">
                    <IconButton onClick={handleClearSearch} size="small">
                      <Clear />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '25px',
                }
              }}
            />

            {/* Drop-down overlay - Fixed positioning to prevent layout shifts */}
            {showSuggestions && ( (searchTerm.trim() && filteredEvents.length > 0) || (!searchTerm.trim() && recentSearches.length > 0) ) && (
              <Paper
                sx={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  right: 0,
                  zIndex: 2000,
                  maxHeight: '320px',
                  overflow: 'auto',
                  boxShadow: '0 8px 20px rgba(0,0,0,0.08)',
                  borderRadius: 2,
                  mt: 1,
                  // Prevent layout shifts
                  transform: 'translateZ(0)', // Force hardware acceleration
                  willChange: 'opacity, transform', // Optimize for animations
                  // Smooth transitions
                  opacity: suggestionsVisible ? 1 : 0,
                  transition: 'opacity 0.15s ease-in-out',
                  // Ensure it doesn't affect document flow
                  pointerEvents: suggestionsVisible ? 'auto' : 'none'
                }}
              >
                {/* When typing: show search results */}
                {searchTerm.trim() ? (
                  <>
                    <Box px={1} pt={1}>
                      <Typography variant="subtitle2" color="text.secondary">Results</Typography>
                    </Box>

                    <List dense disablePadding>
                      {filteredEvents.map((event, index) => {
                        const location = getLocationLabel(event);
                        
                        return (
                          <ListItem
                            key={`${event.title}-${index}`}
                            component="div"
                            onClick={() => handleSuggestionClick(event)}
                            sx={{
                              py: 0.5,
                              px: 1,
                              cursor: 'pointer',
                              borderRadius: 0.5,
                              minHeight: 'auto',
                              '&:hover': { backgroundColor: 'action.hover' }
                            }}
                          >
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <Search fontSize="small" />
                            </ListItemIcon>
                            
                            <ListItemText
                              primary={
                                <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                                  {event.title}
                                </Typography>
                              }
                              secondary={
                                <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                                  {location && `${location} • `}{(event as any).status || ''}
                                </Typography>
                              }
                            />
                          </ListItem>
                        );
                      })}
                    </List>
                  </>
                ) : (
                  // When empty: show recent searches
                  <>
                    <Box px={1} pt={1}>
                      <Typography variant="subtitle2" color="text.secondary">Recent Searches</Typography>
                    </Box>

                    <List dense>
                      {recentSearches.map((s, idx) => (
                        <ListItem
                          key={idx}
                          component="div"
                          onClick={() => {
                            handleSearchChange(s);
                            // simulate selecting the suggestion text and searching immediately
                            setShowSuggestions(false);
                            addToRecentSearches(s);
                            // set filtered results based on this string so parent receives results
                            setSearchTerm(s);
                            const matches = allEvents.filter(evt =>
                              (evt.title || '').toLowerCase().includes(s.toLowerCase())
                            );
                            setFilteredEvents(matches);
                            onSearchResults(matches);
                          }}
                          sx={{ px: 1.25, py: 1, cursor: 'pointer', '&:hover': { backgroundColor: 'action.hover' } }}
                        >
                          <ListItemIcon><Search fontSize="small" /></ListItemIcon>
                          <ListItemText primary={s} />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}
              </Paper>
            )}
          </Box>
        </FlexBox>

        {showFilters && (
          <FlexBox
            gap={2}
            alignItems="center"
            sx={{
              flex: { xs: '1 1 100%', md: '0 1 auto' },
              minWidth: { xs: '100%', md: 'auto' },
              flexWrap: 'nowrap',
              justifyContent: { xs: 'flex-start', md: 'flex-end' }
            }}
          >
            <FormControl size="small" sx={{ minWidth: 120, '& .MuiOutlinedInput-root': { height: 44 }, '& .MuiSelect-select': { display: 'flex', alignItems: 'center', py: 0 } }}>
              <InputLabel>Year</InputLabel>
              <Select value={selectedYear} label="Year" onChange={(e) => { setSelectedYear(e.target.value); onYearFilter(e.target.value); }}>
                <MenuItem value="all">All Years</MenuItem>
                {availableYears.map(y => <MenuItem key={y} value={y}>{y}</MenuItem>)}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120, '& .MuiOutlinedInput-root': { height: 44 }, '& .MuiSelect-select': { display: 'flex', alignItems: 'center', py: 0 } }}>
              <InputLabel>Status</InputLabel>
              <Select value={selectedStatus} label="Status" onChange={(e) => setSelectedStatus(e.target.value)}>
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="accepted">Approved</MenuItem>
                <MenuItem value="submitted">Pending</MenuItem>
                <MenuItem value="rejected">Rejected</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120, '& .MuiOutlinedInput-root': { height: 44 }, '& .MuiSelect-select': { display: 'flex', alignItems: 'center', py: 0 } }}>
              <InputLabel>Type</InputLabel>
              <Select value={selectedType} label="Type" onChange={(e) => setSelectedType(e.target.value)}>
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="external">External</MenuItem>
                <MenuItem value="internal">Internal</MenuItem>
              </Select>
            </FormControl>
          </FlexBox>
        )}
      </FlexBox>

    </Box>
  );
};

export default ProjectSearchBar;