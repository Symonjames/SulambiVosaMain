import React, { useState } from 'react';
import { Box, IconButton, Slide, Fade } from '@mui/material';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import CloseIcon from '@mui/icons-material/Close';
import CompactEventCalendar from '../Analytics/CompactEventCalendar';

const FloatingCalendarButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* Floating Calendar Button */}
      <IconButton
        onClick={handleToggle}
        sx={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '56px',
          height: '56px',
          backgroundColor: '#C07F00',
          color: 'white',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12)',
          zIndex: 1000,
          '&:hover': {
            backgroundColor: '#A06B00',
            transform: 'scale(1.05)',
            boxShadow: '0 6px 16px rgba(0, 0, 0, 0.2), 0 3px 6px rgba(0, 0, 0, 0.15)',
          },
          transition: 'all 0.2s ease-in-out',
          '@media (max-width: 768px)': {
            bottom: '16px',
            right: '16px',
            width: '48px',
            height: '48px',
          }
        }}
      >
        <CalendarTodayIcon sx={{ fontSize: 24 }} />
      </IconButton>

      {/* Backdrop with Blur Effect and Close Button */}
      <Fade in={isOpen} timeout={300}>
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(135deg, rgba(139, 69, 19, 0.3) 0%, rgba(255, 165, 0, 0.2) 100%)',
            backdropFilter: 'blur(8px)',
            zIndex: 1001,
            display: isOpen ? 'block' : 'none'
          }}
          onClick={handleClose}
        >
          {/* Close Button on Background */}
          <IconButton
            onClick={handleClose}
            sx={{
              position: 'absolute',
              top: '20px',
              right: '20px',
              width: '40px',
              height: '40px',
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              color: '#333',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 1)',
                transform: 'scale(1.05)',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
              },
              transition: 'all 0.2s ease-in-out',
              '@media (max-width: 768px)': {
                top: '16px',
                right: '16px',
                width: '36px',
                height: '36px',
              }
            }}
          >
            <CloseIcon sx={{ fontSize: '20px' }} />
          </IconButton>
        </Box>
      </Fade>

      {/* Calendar Widget - Direct Display */}
      <Fade in={isOpen} timeout={300}>
        <Box
          sx={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 1002,
            display: isOpen ? 'block' : 'none',
            backgroundColor: 'white',
            borderRadius: '16px',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15), 0 6px 20px rgba(0, 0, 0, 0.1)',
            padding: '24px',
            maxHeight: '85vh',
            overflow: 'auto',
            '@media (max-width: 768px)': {
              width: '95%',
              maxWidth: '420px',
              padding: '20px',
              borderRadius: '12px',
            },
            '@media (min-width: 769px)': {
              width: 'auto',
              maxWidth: '480px',
              minWidth: '420px',
            }
          }}
        >
          <CompactEventCalendar />
        </Box>
      </Fade>
    </>
  );
};

export default FloatingCalendarButton;
