import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Container,
  Stack
} from '@mui/material';
import {
  VolunteerActivism
} from '@mui/icons-material';
import VolunteerEvaluationForm from '../components/Forms/VolunteerEvaluationForm';
import SulambiLogo from '../components/Icons/SulambiLogo';

const EvaluationDemoPage: React.FC = () => {
  const [openVolunteerForm, setOpenVolunteerForm] = useState(false);
  const [selectedEvent] = useState({
    id: 1,
    title: "Community Cleanup Drive 2024",
    type: "external" as const,
    date: "2024-03-15",
    venue: "Batangas State University Main Campus"
  });

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5', padding: 3 }}>
      <Container maxWidth="md">
        {/* Introduction Section */}
        <Card sx={{ 
          mt: 4, 
          mb: 4, 
          boxShadow: 3,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #C07F00 0%, #FFD700 100%)',
          color: 'white'
        }}>
          <CardContent sx={{ p: 4 }}>
            <Stack spacing={3} alignItems="center" textAlign="center">
              {/* Header with Sulambi Logo */}
              <Box>
                <SulambiLogo />
                <Typography variant="h3" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                  Evaluation Forms
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  Help us improve our programs and services
                </Typography>
              </Box>

              {/* Description */}
              <Typography variant="body1" sx={{ maxWidth: 600, lineHeight: 1.6 }}>
                Your feedback is invaluable in helping us enhance our volunteer programs and community services. 
                Choose the appropriate evaluation form below.
              </Typography>
            </Stack>
          </CardContent>
        </Card>

        {/* Volunteer Evaluation Form Card */}
        <Card sx={{ 
          maxWidth: 500,
          mx: 'auto',
          display: 'flex', 
          flexDirection: 'column',
          boxShadow: 2,
          borderRadius: 2,
          '&:hover': {
            boxShadow: 4,
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease'
          }
        }}>
          <CardContent sx={{ flexGrow: 1, p: 3 }}>
            <Stack spacing={2} alignItems="center" textAlign="center">
              <VolunteerActivism sx={{ fontSize: 50, color: '#C07F00' }} />
              <Typography variant="h5" fontWeight="bold" color="primary">
                Training / Seminar Evaluation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                For participants to evaluate training sessions and seminars
              </Typography>
            </Stack>
          </CardContent>
          <Box sx={{ p: 3, pt: 0 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<VolunteerActivism />}
              onClick={() => setOpenVolunteerForm(true)}
              fullWidth
              sx={{
                backgroundColor: '#C07F00',
                '&:hover': {
                  backgroundColor: '#B07000',
                }
              }}
            >
              Start Training Evaluation
            </Button>
          </Box>
        </Card>

      </Container>

      {/* Volunteer Evaluation Form */}
      <VolunteerEvaluationForm
        open={openVolunteerForm}
        setOpen={setOpenVolunteerForm}
        eventId={selectedEvent.id.toString()}
        eventType={selectedEvent.type}
        eventData={{
          title: selectedEvent.title,
          date: selectedEvent.date,
          venue: selectedEvent.venue
        }}
        zval={6}
      />
    </Box>
  );
};

export default EvaluationDemoPage;































