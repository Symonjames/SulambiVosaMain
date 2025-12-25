import React, { useState, useEffect } from 'react';
import FlexBox from '../FlexBox';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Chip, 
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import { 
  CalendarToday, 
  Event, 
  LocationOn, 
  AccessTime,
  ChevronLeft,
  ChevronRight,
  Today
} from '@mui/icons-material';
import { getAllEvents } from '../../api/events';
import { ExternalEventProposalType, InternalEventProposalType } from '../../interface/types';

const CompactEventCalendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<(ExternalEventProposalType | InternalEventProposalType)[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date());

  useEffect(() => {
    getAllEvents().then((response) => {
      const externalEvents: ExternalEventProposalType[] = response.data.external || [];
      const internalEvents: InternalEventProposalType[] = response.data.internal || [];
      
      const allEvents = [...externalEvents, ...internalEvents].filter(
        (event) => event && event.status === "accepted"
      );
      
      setEvents(allEvents);
    }).catch((error) => {
      console.error('Error fetching events:', error);
      setEvents([]);
    });
  }, []);

  // Get events for the current month
  const getEventsForMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    
    return events.filter(event => {
      const eventDate = new Date(event.durationStart);
      return eventDate.getFullYear() === year && eventDate.getMonth() === month;
    });
  };

  // Get events for a specific date
  const getEventsForDate = (date: Date) => {
    const dateStr = date.toDateString();
    return events.filter(event => {
      const eventDate = new Date(event.durationStart);
      return eventDate.toDateString() === dateStr;
    });
  };

  // Get upcoming events (next 7 days)
  const getUpcomingEvents = () => {
    const today = new Date();
    const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    return events.filter(event => {
      const eventDate = new Date(event.durationStart);
      return eventDate >= today && eventDate <= nextWeek;
    }).sort((a, b) => new Date(a.durationStart).getTime() - new Date(b.durationStart).getTime());
  };

  // Calendar navigation
  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1);
      } else {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    });
  };

  // Get calendar days
  const getCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    for (let i = 0; i < 42; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      days.push(date);
    }
    return days;
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const calendarDays = getCalendarDays();
  const monthEvents = getEventsForMonth(currentDate);
  const upcomingEvents = getUpcomingEvents();

  return (
    <FlexBox
      flexDirection="column"
      minHeight="380px"
      flex="0 0 auto"
      sx={{
        width: '100%',
        '@media (max-width: 768px)': {
          width: '100%',
        }
      }}
    >
      <Typography textAlign="center" fontWeight="bold" gutterBottom variant="h6" sx={{ fontSize: '20px' }}>
        <CalendarToday sx={{ mr: 1, verticalAlign: 'middle', fontSize: 24 }} />
        Event Calendar
      </Typography>

      {/* Calendar Header */}
      <FlexBox justifyContent="space-between" alignItems="center" mb={3}>
        <IconButton onClick={() => navigateMonth('prev')} size="medium" sx={{ fontSize: '20px' }}>
          <ChevronLeft sx={{ fontSize: '20px' }} />
        </IconButton>
        <Typography variant="h6" fontWeight="bold" sx={{ fontSize: '18px' }}>
          {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
        </Typography>
        <IconButton onClick={() => navigateMonth('next')} size="medium" sx={{ fontSize: '20px' }}>
          <ChevronRight sx={{ fontSize: '20px' }} />
        </IconButton>
      </FlexBox>

      {/* Calendar Grid */}
      <Box mb={2}>
        {/* Day headers */}
        <FlexBox justifyContent="space-between" mb={1}>
          {dayNames.map(day => (
            <Typography key={day} variant="body2" textAlign="center" width="14.28%" fontWeight="bold" sx={{ fontSize: '14px' }}>
              {day}
            </Typography>
          ))}
        </FlexBox>

        {/* Calendar days */}
        <Box display="grid" gridTemplateColumns="repeat(7, 1fr)" gap={0.75}>
          {calendarDays.map((date, index) => {
            const isCurrentMonth = date.getMonth() === currentDate.getMonth();
            const isToday = date.toDateString() === new Date().toDateString();
            const isSelected = date.toDateString() === selectedDate.toDateString();
            const dayEvents = getEventsForDate(date);
            
            return (
              <Box
                key={index}
                onClick={() => setSelectedDate(date)}
                sx={{
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  borderRadius: '6px',
                  backgroundColor: isSelected ? '#2196f3' : isToday ? '#e3f2fd' : 'transparent',
                  color: isCurrentMonth ? (isSelected ? 'white' : 'text.primary') : 'text.disabled',
                  fontWeight: isToday ? 'bold' : 'normal',
                  position: 'relative',
                  '&:hover': {
                    backgroundColor: isSelected ? '#1976d2' : '#f5f5f5',
                  }
                }}
              >
                <Typography variant="body2" sx={{ fontSize: '14px' }}>
                  {date.getDate()}
                </Typography>
                {dayEvents.length > 0 && (
                  <Box
                    sx={{
                      position: 'absolute',
                      bottom: '2px',
                      width: '4px',
                      height: '4px',
                      borderRadius: '50%',
                      backgroundColor: isSelected ? 'white' : '#4caf50',
                    }}
                  />
                )}
              </Box>
            );
          })}
        </Box>
      </Box>

      <Divider sx={{ my: 1 }} />

      {/* Selected Date Events */}
      <Box mb={2}>
        <Typography variant="body2" fontWeight="bold" gutterBottom sx={{ fontSize: '14px' }}>
          Events on {selectedDate.toLocaleDateString()}:
        </Typography>
        {getEventsForDate(selectedDate).length > 0 ? (
          <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
            {getEventsForDate(selectedDate).map((event, index) => (
              <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 20 }}>
                  <Event sx={{ fontSize: 16, color: '#4caf50' }} />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" fontWeight="medium" sx={{ fontSize: '12px' }}>
                      {event.title}
                    </Typography>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '11px' }}>
                        <LocationOn sx={{ fontSize: 12, mr: 0.5 }} />
                        {(event as ExternalEventProposalType).location || (event as InternalEventProposalType).venue}
                      </Typography>
                      <br />
                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '11px' }}>
                        <AccessTime sx={{ fontSize: 12, mr: 0.5 }} />
                        {new Date(event.durationStart).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ fontSize: '12px' }}>
            No events scheduled
          </Typography>
        )}
      </Box>

      <Divider sx={{ my: 1 }} />

      {/* Upcoming Events */}
      <Box>
        <Typography variant="body2" fontWeight="bold" gutterBottom sx={{ fontSize: '14px' }}>
          <Today sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
          Upcoming (Next 7 Days):
        </Typography>
        {upcomingEvents.length > 0 ? (
          <List dense sx={{ maxHeight: 100, overflow: 'auto' }}>
            {upcomingEvents.slice(0, 3).map((event, index) => (
              <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 20 }}>
                  <Event sx={{ fontSize: 16, color: '#ff9800' }} />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" fontWeight="medium" sx={{ fontSize: '12px' }}>
                      {event.title}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '11px' }}>
                      {new Date(event.durationStart).toLocaleDateString()} at{' '}
                      {new Date(event.durationStart).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
            {upcomingEvents.length > 3 && (
              <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ fontSize: '12px' }}>
                +{upcomingEvents.length - 3} more events
              </Typography>
            )}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ fontSize: '12px' }}>
            No upcoming events
          </Typography>
        )}
      </Box>
    </FlexBox>
  );
};

export default CompactEventCalendar;


