import React, { useState, useContext, useEffect, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Typography, Card, CardContent, Box, Chip, Container } from "@mui/material";
import FlexBox from "../components/FlexBox";
import BeneficiariesEvaluationForm from "../components/Forms/BeneficiariesEvaluationForm";
import { SnackbarContext } from "../contexts/SnackbarProvider";
import { People, Assignment, ArrowBack } from "@mui/icons-material";
import PrimaryButton from "../components/Buttons/PrimaryButton";
import dayjs from "dayjs";
import { getAllPublicEvents } from "../api/events";

interface PublicEvent {
  id: number;
  title: string;
  durationStart: string;
  durationEnd: string;
  venue?: string;
  location?: string;
  eventTypeIndicator?: "external" | "internal";
  eventType?: "external" | "internal";
  status?: string;
}

interface EvaluationEventOption {
  id: number;
  title: string;
  durationStart: string;
  durationEnd: string;
  venue?: string;
  location?: string;
  eventType: "external" | "internal";
}

const BeneficiaryEvaluationPage = () => {
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [openForm, setOpenForm] = useState(false);
  const [eligibleEvents, setEligibleEvents] = useState<EvaluationEventOption[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);

  useEffect(() => {
    const fetchEligibleEvents = async () => {
      setEventsLoading(true);
      try {
        const response = await getAllPublicEvents();
        const externalEvents: PublicEvent[] = response.data.external ?? [];
        const internalEvents: PublicEvent[] = response.data.internal ?? [];
        const combined: PublicEvent[] = [...externalEvents, ...internalEvents];

        const now = dayjs();
        // Events can be evaluated for 1 week (7 days) after they end
        // Show events that ended within the last 7 days
        const filtered = combined
          .filter((event) => {
            // durationEnd is stored as milliseconds (INTEGER) in the database
            // dayjs can parse both milliseconds and date strings
            let end;
            if (typeof event.durationEnd === 'number') {
              // If it's a number (timestamp in milliseconds), use it directly
              end = dayjs(event.durationEnd);
            } else if (typeof event.durationEnd === 'string') {
              // If it's a string, parse it
              end = dayjs(event.durationEnd);
            } else {
              return false;
            }
            
            const isValid = end.isValid();
            if (!isValid) return false;
            
            // Check if event has ended (end time is before or equal to current time)
            const hasEnded = end.valueOf() <= now.valueOf();
            
            // Check if event ended within the last 7 days (1 week evaluation window)
            // Use hours for more precise calculation (7 days = 168 hours)
            const hoursSinceEnd = now.diff(end, 'hour', true);
            const withinOneWeek = hoursSinceEnd >= 0 && hoursSinceEnd <= 168; // 7 days = 168 hours
            
            return hasEnded && withinOneWeek;
          })
          .map((event) => ({
            id: event.id,
            title: event.title,
            durationStart: event.durationStart,
            durationEnd: event.durationEnd,
            venue: event.venue,
            location: event.location,
            eventType:
              event.eventTypeIndicator ?? event.eventType ?? "external",
          }))
          .sort((a, b) =>
            dayjs(b.durationEnd).valueOf() - dayjs(a.durationEnd).valueOf()
          );
        
        setEligibleEvents(filtered);
      } catch (error) {
        console.error("Error loading events for beneficiary evaluation", error);
        showSnackbarMessage(
          "Unable to load events available for evaluation.",
          "error"
        );
      } finally {
        setEventsLoading(false);
      }
    };

    fetchEligibleEvents();
  }, [showSnackbarMessage]);
  
  const preselectedEventId = useMemo(() => searchParams.get("eventId"), [searchParams]);

  const handleSubmit = (data: any) => {
    showSnackbarMessage("Beneficiary evaluation submitted successfully!", "success");
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
          background: "linear-gradient(135deg, #9c27b0 0%, #e91e63 100%)",
          borderRadius: "20px",
          padding: "40px 20px",
          boxShadow: "0 10px 30px rgba(156, 39, 176, 0.3)",
        }}
      >
        {/* Header Section */}
        <FlexBox flexDirection="column" alignItems="center" rowGap="20px">
          <FlexBox alignItems="center" gap="15px">
            <People sx={{ fontSize: 60, color: "white" }} />
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
                Beneficiary Evaluation
              </Typography>
              <Typography 
                variant="h6" 
                sx={{ 
                  color: "rgba(255, 255, 255, 0.9)",
                  textAlign: "center"
                }}
              >
                Community Service Feedback Form
              </Typography>
            </Box>
          </FlexBox>
          
          <Chip 
            label="BENEFICIARY FORM" 
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

        {/* Description Card */}
        <Card
          sx={{
            maxWidth: 600,
            width: "100%",
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(10px)",
            borderRadius: "15px",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Typography
              variant="h6"
              gutterBottom
              sx={{ fontWeight: "bold", color: "#7b1fa2" }}
            >
              About This Evaluation
            </Typography>
            <Typography variant="body1" paragraph>
              Help us improve our community services by sharing your experience
              as a service recipient. Your feedback is essential in enhancing
              the quality and impact of our volunteer programs. Events can be
              evaluated for one week after they conclude. You can evaluate any
              finished event within this window - no account or membership required.
              Simply select the event you participated in and share your feedback.
            </Typography>

            <Box sx={{ mt: 3 }}>
              <Typography
                variant="subtitle2"
                gutterBottom
                sx={{ fontWeight: "bold" }}
              >
                What you'll evaluate:
              </Typography>
              <Box component="ul" sx={{ pl: 2, m: 0 }}>
                <li>Service quality & impact</li>
                <li>Volunteer helpfulness & friendliness</li>
                <li>Accessibility & participation</li>
                <li>Cultural sensitivity & respect</li>
                <li>Overall service experience</li>
              </Box>
            </Box>

            <FlexBox gap={1} flexWrap="wrap" mt={3}>
              <Chip label="Impact Assessment" size="small" color="secondary" />
              <Chip label="Service Quality" size="small" color="secondary" />
              <Chip label="Accessibility" size="small" color="secondary" />
              <Chip label="Community Impact" size="small" color="secondary" />
            </FlexBox>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <FlexBox gap="20px" flexWrap="wrap" justifyContent="center">
          <PrimaryButton
            label="Start Beneficiary Evaluation"
            icon={<Assignment />}
            onClick={() => {
              if (eligibleEvents.length === 0) {
                showSnackbarMessage(
                  "No recently finished events are currently available for evaluation.",
                  "info"
                );
                return;
              }
              setOpenForm(true);
            }}
            sx={{
              backgroundColor: "#7b1fa2",
              "&:hover": {
                backgroundColor: "#4a148c"
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
      <BeneficiariesEvaluationForm
        open={openForm}
        setOpen={setOpenForm}
        availableEvents={eligibleEvents}
        initialEventId={preselectedEventId ?? undefined}
        onSubmit={handleSubmit}
        isLoadingEvents={eventsLoading}
      />
    </Container>
  );
};

export default BeneficiaryEvaluationPage;