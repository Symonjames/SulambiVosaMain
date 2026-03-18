import React from "react";
import {
  Box,
  Typography,
  IconButton,
  Dialog,
  DialogContent,
  DialogTitle,
  Button,
  Stack
} from "@mui/material";
import {
  Close as CloseIcon,
  Send
} from "@mui/icons-material";
import SulambiLogo from "../Icons/SulambiLogo";

interface BaseEvaluationFormProps {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle: string;
  formContent: React.ReactNode;
  onSubmit: (data: any) => void;
  submitButtonText?: string;
  isLoading?: boolean;
}

const BaseEvaluationForm: React.FC<BaseEvaluationFormProps> = ({
  open,
  onClose,
  title,
  subtitle,
  formContent,
  onSubmit,
  submitButtonText = "Submit Evaluation",
  isLoading = false
}) => {
  const handleSubmit = () => {
    // This will be handled by the parent component
    onSubmit({});
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      sx={{
        '& .MuiDialog-paper': {
          borderRadius: '16px',
          background: 'linear-gradient(135deg, #C07F00 0%, #FFD700 100%)',
          color: 'white',
          minHeight: '80vh',
          maxHeight: '90vh'
        }
      }}
      PaperProps={{
        sx: {
          boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
          border: '2px solid rgba(255,255,255,0.2)'
        }
      }}
    >
      <DialogTitle sx={{ 
        background: 'rgba(255,255,255,0.1)', 
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255,255,255,0.2)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        p: 3
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ 
            transform: 'scale(1.8)',
            display: 'flex',
            alignItems: 'center'
          }}>
            <SulambiLogo />
          </Box>
          <Box>
            <Typography variant="h4" fontWeight="bold">
              {title}
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9, fontSize: '1.1rem' }}>
              {subtitle}
            </Typography>
          </Box>
        </Box>
        <IconButton
          onClick={onClose}
          sx={{
            color: 'white',
            backgroundColor: 'rgba(255,255,255,0.2)',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.3)'
            }
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ 
        p: 0,
        backgroundColor: 'rgba(255,255,255,0.95)',
        color: 'text.primary',
        margin: '16px',
        borderRadius: '12px',
        minHeight: '60vh',
        maxHeight: '70vh',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <Box sx={{ 
          p: 3,
          overflow: 'auto',
          flex: 1,
          '&::-webkit-scrollbar': {
            width: '10px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'rgba(0,0,0,0.1)',
            borderRadius: '5px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#C07F00',
            borderRadius: '5px',
            '&:hover': {
              background: '#B07000',
            },
          },
        }}>
          {formContent}
        </Box>
        
        {/* Submit Button */}
        <Box sx={{
          p: 3,
          backgroundColor: 'rgba(255,255,255,0.95)',
          borderTop: '1px solid rgba(0,0,0,0.1)',
          borderRadius: '0 0 12px 12px'
        }}>
          <Stack direction="row" justifyContent="center">
            <Button
              variant="contained"
              size="large"
              startIcon={<Send />}
              onClick={handleSubmit}
              disabled={isLoading}
              sx={{
                backgroundColor: '#C07F00',
                color: 'white',
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(192, 127, 0, 0.3)',
                '&:hover': {
                  backgroundColor: '#B07000',
                  boxShadow: '0 6px 16px rgba(192, 127, 0, 0.4)',
                  transform: 'translateY(-2px)',
                  transition: 'all 0.3s ease'
                },
                '&:disabled': {
                  backgroundColor: 'rgba(192, 127, 0, 0.5)',
                  color: 'rgba(255, 255, 255, 0.7)'
                }
              }}
            >
              {isLoading ? 'Submitting...' : submitButtonText}
            </Button>
          </Stack>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default BaseEvaluationForm;
