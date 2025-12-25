import React from 'react';
import { Box, IconButton, Typography, Slide, Fade } from '@mui/material';
import { Close } from '@mui/icons-material';
import FlexBox from '../FlexBox';

interface CurtainPanelProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  direction?: 'down' | 'right' | 'left';
  maxHeight?: string;
  maxWidth?: string;
}

const CurtainPanel: React.FC<CurtainPanelProps> = ({
  open,
  onClose,
  title,
  children,
  direction = 'down',
  maxHeight = '80vh',
  maxWidth = '90vw'
}) => {
  const getSlideProps = () => {
    switch (direction) {
      case 'right':
        return { direction: 'left' as const, in: open };
      case 'left':
        return { direction: 'right' as const, in: open };
      default:
        return { direction: 'up' as const, in: open };
    }
  };

  return (
    <>
      {/* Backdrop */}
      <Fade in={open}>
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(135deg, rgba(139, 69, 19, 0.3) 0%, rgba(255, 165, 0, 0.2) 100%)',
            backdropFilter: 'blur(8px)',
            zIndex: 1000,
            display: open ? 'block' : 'none'
          }}
          onClick={onClose}
        />
      </Fade>

      {/* Curtain Panel */}
      <Fade in={open} timeout={300}>
        <Box
          sx={{
            position: 'fixed',
            top: maxWidth && maxWidth !== '90vw' ? '50%' : (direction === 'down' ? 0 : 'auto'),
            bottom: maxWidth && maxWidth !== '90vw' ? 'auto' : (direction === 'down' ? 'auto' : 0),
            left: maxWidth && maxWidth !== '90vw' ? '50%' : (direction === 'right' ? 'auto' : 0),
            right: maxWidth && maxWidth !== '90vw' ? 'auto' : (direction === 'left' ? 'auto' : 0),
            transform: maxWidth && maxWidth !== '90vw' ? 'translate(-50%, -50%)' : 'none',
            width: direction === 'down' && (!maxWidth || maxWidth === '90vw') ? '100%' : maxWidth,
            height: direction === 'down' && (!maxWidth || maxWidth === '90vw') ? maxHeight : '100%',
            maxHeight: maxWidth && maxWidth !== '90vw' ? maxHeight : 'none',
            backgroundColor: 'white',
            boxShadow: maxWidth && maxWidth !== '90vw' ? '0 12px 40px rgba(0, 0, 0, 0.15), 0 6px 20px rgba(0, 0, 0, 0.1)' : '0 -4px 20px rgba(0, 0, 0, 0.15)',
            borderRadius: maxWidth && maxWidth !== '90vw' ? '16px' : '0px',
            zIndex: 1001,
            display: open ? 'flex' : 'none',
            flexDirection: 'column',
            overflow: 'hidden',
            '@media (max-width: 768px)': {
              width: maxWidth && maxWidth !== '90vw' ? '95%' : (direction === 'down' ? '100%' : maxWidth),
              maxWidth: maxWidth && maxWidth !== '90vw' ? '420px' : 'none',
              borderRadius: maxWidth && maxWidth !== '90vw' ? '12px' : '0px',
            }
          }}
        >
          {/* Header */}
          <FlexBox
            justifyContent="space-between"
            alignItems="center"
            p={2}
            sx={{
              borderBottom: maxWidth && maxWidth !== '90vw' ? 'none' : '1px solid #e0e0e0',
              backgroundColor: maxWidth && maxWidth !== '90vw' ? 'transparent' : '#f8f9fa',
              minHeight: '60px',
              position: maxWidth && maxWidth !== '90vw' ? 'relative' : 'static',
              '&::after': maxWidth && maxWidth !== '90vw' ? {
                content: '""',
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: '1px',
                background: 'linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.1) 50%, transparent 100%)',
              } : {}
            }}
          >
            <Typography variant="h6" fontWeight="bold">
              {title}
            </Typography>
            <IconButton
              onClick={onClose}
              size="small"
              sx={{
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.2)'
                }
              }}
            >
              <Close />
            </IconButton>
          </FlexBox>

          {/* Content */}
          <Box
            sx={{
              flex: 1,
              overflow: 'auto',
              p: 2
            }}
          >
            {children}
          </Box>
        </Box>
      </Fade>
    </>
  );
};

export default CurtainPanel;
