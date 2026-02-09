import React, { useState, useContext, useEffect, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Typography, Card, CardContent, Box, Chip, Container } from "@mui/material";
import FlexBox from "../components/FlexBox";
import BeneficiariesEvaluationForm from "../components/Forms/BeneficiariesEvaluationForm";
import { SnackbarContext } from "../contexts/SnackbarProvider";
import { People, Assignment, ArrowBack } from "@mui/icons-material";
import PrimaryButton from "../components/Buttons/PrimaryButton";
import dayjs from "dayjs";
import { getBeneficiaryEligibleEvents } from "../api/events";

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
  requiresBeneficiaryPin?: boolean;
}

interface EvaluationEventOption {
  id: number;
  title: string;
  durationStart: string;
  durationEnd: string;
  venue?: string;
  location?: string;
  eventType: "external" | "internal";
  requiresBeneficiaryPin?: boolean;
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
        const response = await getBeneficiaryEligibleEvents();
        const externalEvents: PublicEvent[] = response.data.external ?? [];
        const internalEvents: PublicEvent[] = response.data.internal ?? [];
        const combined: PublicEvent[] = [...externalEvents, ...internalEvents];

        const mapped: EvaluationEventOption[] = combined
          .map((event) => ({
            id: event.id,
            title: event.title,
            durationStart: event.durationStart,
            durationEnd: event.durationEnd,
            venue: event.venue,
            location: event.location,
            eventType:
              event.eventTypeIndicator ?? event.eventType ?? "external",
            requiresBeneficiaryPin: !!event.requiresBeneficiaryPin,
          }))
          .sort((a, b) =>
            dayjs(b.durationEnd).valueOf() - dayjs(a.durationEnd).valueOf()
          );

        setEligibleEvents(mapped);
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
          background: "linear-gradient(to right, #f5b000, #e9a100, #d98a00)",
          borderRadius: "20px",
          padding: "40px 20px",
          boxShadow: "0 10px 30px rgba(212, 168, 75, 0.35)",
        }}
      >
        {/* Header Section */}
        <FlexBox flexDirection="column" alignItems="center" rowGap="20px">
          <FlexBox alignItems="center" gap="15px">
            <People sx={{ fontSize: 60, color: "#5d4e37" }} />
            <Box>
              <Typography 
                variant="h3" 
                component="h1" 
                sx={{ 
                  color: "#3d3428", 
                  fontWeight: "bold",
                  textAlign: "center"
                }}
              >
                Beneficiary Evaluation
              </Typography>
              <Typography 
                variant="h6" 
                sx={{ 
                  color: "rgba(61, 52, 40, 0.85)",
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
              backgroundColor: "rgba(212, 168, 75, 0.4)",
              color: "#3d3428",
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
              sx={{ fontWeight: "bold", color: "#b8860b" }}
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
              <Chip label="Impact Assessment" size="small" sx={{ backgroundColor: "#d4a84b", color: "#fff" }} />
              <Chip label="Service Quality" size="small" sx={{ backgroundColor: "#d4a84b", color: "#fff" }} />
              <Chip label="Accessibility" size="small" sx={{ backgroundColor: "#d4a84b", color: "#fff" }} />
              <Chip label="Community Impact" size="small" sx={{ backgroundColor: "#d4a84b", color: "#fff" }} />
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
              background: "linear-gradient(to right, #f5b000, #e9a100, #d98a00)",
              color: "#fff",
              "&:hover": {
                background: "linear-gradient(to right, #e9a100, #d98a00, #c47800)",
                color: "#fff"
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
              borderColor: "rgba(245, 176, 0, 0.6)",
              color: "#b8860b",
              "&:hover": {
                background: "linear-gradient(to right, #e9a100, #d98a00, #c47800)",
                borderColor: "transparent",
                color: "#fff"
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