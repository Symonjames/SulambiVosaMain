import React, { useState, useContext } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Typography, Card, CardContent, Box, Chip, Container } from "@mui/material";
import FlexBox from "../components/FlexBox";
import VolunteerEvaluationForm from "../components/Forms/VolunteerEvaluationForm";
import { SnackbarContext } from "../contexts/SnackbarProvider";
import { VolunteerActivism, Star, Assignment, ArrowBack } from "@mui/icons-material";
import PrimaryButton from "../components/Buttons/PrimaryButton";

const VolunteerEvaluationPage = () => {
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [openForm, setOpenForm] = useState(false);
  
  // Get event data from URL params or use defaults
  const eventId = searchParams.get('eventId') || "1";
  const eventTitle = searchParams.get('title') || "Volunteer Training Program";
  const eventDate = searchParams.get('date') || new Date().toLocaleDateString();
  const eventVenue = searchParams.get('venue') || "TBA";

  const eventData = {
    title: eventTitle,
    date: eventDate,
    venue: eventVenue
  };

  const handleSubmit = (data: any) => {
    console.log('Volunteer Evaluation Submitted:', data);
    showSnackbarMessage("Volunteer evaluation submitted successfully!", "success");
    setOpenForm(false);
    // Navigate back or to thank you page
    setTimeout(() => {
      navigate('/feedback-message');
    }, 2000);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <FlexBox
        flexDirection="column"
        alignItems="center"
        rowGap="30px"
        sx={{
          minHeight: "80vh",
          background: "linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)",
          borderRadius: "20px",
          padding: "40px 20px",
          boxShadow: "0 10px 30px rgba(76, 175, 80, 0.3)",
        }}
      >
        {/* Header Section */}
        <FlexBox flexDirection="column" alignItems="center" rowGap="20px">
          <FlexBox alignItems="center" gap="15px">
            <VolunteerActivism sx={{ fontSize: 60, color: "white" }} />
            <Box>
              <Typography 
                variant="h3" 
                component="h1" 
                sx={{ 
                  color: "white", 
                  fontWeight: "bold",
                  textAlign: "center"
                }}
              >
                Volunteer Evaluation
              </Typography>
              <Typography 
                variant="h6" 
                sx={{ 
                  color: "rgba(255, 255, 255, 0.9)",
                  textAlign: "center"
                }}
              >
                Training & Seminar Feedback Form
              </Typography>
            </Box>
          </FlexBox>
          
          <Chip 
            label="VOLUNTEER FORM" 
            sx={{ 
              backgroundColor: "rgba(255, 255, 255, 0.2)",
              color: "white",
              fontWeight: "bold",
              fontSize: "0.9rem",
              px: 2,
              py: 1
            }} 
          />
        </FlexBox>

        {/* Event Information Card */}
        <Card 
          sx={{ 
            maxWidth: 600, 
            width: "100%",
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(10px)",
            borderRadius: "15px",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)"
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: "bold", color: "#2e7d32" }}>
              Event Information
            </Typography>
            <Box sx={{ display: "grid", gap: 2, mt: 2 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Event Title:
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: "medium" }}>
                  {eventData.title}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Date:
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: "medium" }}>
                  {eventData.date}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Venue:
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: "medium" }}>
                  {eventData.venue}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Description Card */}
        <Card 
          sx={{ 
            maxWidth: 600, 
            width: "100%",
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(10px)",
            borderRadius: "15px",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)"
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: "bold", color: "#2e7d32" }}>
              About This Evaluation
            </Typography>
            <Typography variant="body1" paragraph>
              Help us improve our volunteer training and seminar programs by sharing your experience. 
              Your feedback is valuable in enhancing future volunteer opportunities and community service initiatives.
            </Typography>
            
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: "bold" }}>
                What you'll evaluate:
              </Typography>
              <Box component="ul" sx={{ pl: 2, m: 0 }}>
                <li>Event organization & planning</li>
                <li>Learning & skill development</li>
                <li>Team collaboration & support</li>
                <li>Training materials & resources</li>
                <li>Overall volunteer experience</li>
              </Box>
            </Box>

            <FlexBox gap={1} flexWrap="wrap" mt={3}>
              <Chip label="Rating System" size="small" color="success" />
              <Chip label="Skill Development" size="small" color="success" />
              <Chip label="Team Work" size="small" color="success" />
              <Chip label="Training Quality" size="small" color="success" />
            </FlexBox>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <FlexBox gap="20px" flexWrap="wrap" justifyContent="center">
          <PrimaryButton
            label="Start Volunteer Evaluation"
            icon={<Star />}
            onClick={() => setOpenForm(true)}
            sx={{
              backgroundColor: "#2e7d32",
              "&:hover": {
                backgroundColor: "#1b5e20"
              },
              px: 4,
              py: 1.5,
              fontSize: "1.1rem"
            }}
          />
          
          <PrimaryButton
            label="Back to Home"
            icon={<ArrowBack />}
            variant="outlined"
            onClick={() => navigate('/')}
            sx={{
              borderColor: "white",
              color: "white",
              "&:hover": {
                borderColor: "white",
                backgroundColor: "rgba(255, 255, 255, 0.1)"
              },
              px: 4,
              py: 1.5,
              fontSize: "1.1rem"
            }}
          />
        </FlexBox>
      </FlexBox>

      {/* Evaluation Form Modal */}
      <VolunteerEvaluationForm
        open={openForm}
        setOpen={setOpenForm}
        eventId={eventId}
        eventType="external"
        eventData={eventData}
        onSubmit={handleSubmit}
      />
    </Container>
  );
};

export default VolunteerEvaluationPage;