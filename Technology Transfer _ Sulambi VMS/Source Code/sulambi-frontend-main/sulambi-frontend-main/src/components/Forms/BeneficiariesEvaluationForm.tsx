import React, { useState, useRef, useMemo, useEffect } from "react";
import { useContext } from "react";
import BaseEvaluationForm from "./BaseEvaluationForm";
import BeneficiariesRawEvalForm from "./raw/BeneficiariesRawEvalForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { evaluationAnalyticsService, BeneficiaryEvaluationData } from "../../services/evaluationAnalytics";
import dayjs from "dayjs";
import { Box, Typography } from "@mui/material";
import CustomDropdown from "../Inputs/CustomDropdown";
import FlexBox from "../FlexBox";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

interface Props {
  open: boolean;
  zval?: number;
  setOpen?: (state: boolean) => void;
  eventId?: string;
  eventType?: 'external' | 'internal';
  eventData?: {
    title?: string;
    date?: string;
    venue?: string;
  };
  onSubmit?: (data: any) => void;
  availableEvents?: EvaluationEventOption[];
  initialEventId?: string;
  isLoadingEvents?: boolean;
}

interface EvaluationEventOption {
  id: number;
  title: string;
  durationStart: string;
  durationEnd: string;
  venue?: string;
  location?: string;
  eventType: 'external' | 'internal';
}

const BeneficiariesEvaluationForm: React.FC<Props> = ({ 
  open, 
  setOpen, 
  eventId = "1",
  eventType = "external",
  eventData,
  onSubmit,
  availableEvents = [],
  initialEventId,
  isLoadingEvents
}: Props) => {
  const { formData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const [isLoading, setIsLoading] = useState(false);
  const startTimeRef = useRef<number>(Date.now());
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      startTimeRef.current = Date.now();
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;

    if (availableEvents.length === 0) {
      setSelectedEventId(null);
      return;
    }

    if (initialEventId) {
      const match = availableEvents.find(
        (option) => option.id.toString() === initialEventId
      );
      if (match) {
        setSelectedEventId(match.id.toString());
        return;
      }
    }

    setSelectedEventId(availableEvents[0].id.toString());
  }, [availableEvents, initialEventId, open]);

  const selectedEvent = useMemo(() => {
    if (!selectedEventId) {
      return undefined;
    }
    return availableEvents.find(
      (option) => option.id.toString() === selectedEventId
    );
  }, [availableEvents, selectedEventId]);

  const evaluationWindowSummary = useMemo(() => {
    if (!selectedEvent) return null;
    const end = dayjs(selectedEvent.durationEnd);
    if (!end.isValid()) return null;
    return {
      end: end.format("MMMM D, YYYY h:mm A"),
    };
  }, [selectedEvent]);

  const handleClose = () => {
    if (setOpen) {
      setOpen(false);
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    
    try {
      if (!selectedEvent) {
        if (availableEvents.length === 0) {
          showSnackbarMessage(
            "There are no finished events available for evaluation right now.",
            "warning"
          );
        } else {
          showSnackbarMessage(
            "Please select a finished event to evaluate.",
            "warning"
          );
        }
        setIsLoading(false);
        return;
      }

      // Extract form data and convert to BeneficiaryEvaluationData format
      const beneficiaryData: BeneficiaryEvaluationData = {
        overallSatisfaction: formData.criteria?.overall === "Excellent" ? 5 : 
                           formData.criteria?.overall === "Very Satisfactory" ? 4 :
                           formData.criteria?.overall === "Satisfactory" ? 3 :
                           formData.criteria?.overall === "Fair" ? 2 : 1,
        serviceQuality: formData.criteria?.appropriateness === "Excellent" ? 5 : 
                       formData.criteria?.appropriateness === "Very Satisfactory" ? 4 :
                       formData.criteria?.appropriateness === "Satisfactory" ? 3 :
                       formData.criteria?.appropriateness === "Fair" ? 2 : 1,
        volunteerHelpfulness: formData.criteria?.expectations === "Excellent" ? 5 : 
                             formData.criteria?.expectations === "Very Satisfactory" ? 4 :
                             formData.criteria?.expectations === "Satisfactory" ? 3 :
                             formData.criteria?.expectations === "Fair" ? 2 : 1,
        impactOnCommunity: formData.criteria?.session === "Excellent" ? 5 : 
                          formData.criteria?.session === "Very Satisfactory" ? 4 :
                          formData.criteria?.session === "Satisfactory" ? 3 :
                          formData.criteria?.session === "Fair" ? 2 : 1,
        accessibility: formData.criteria?.time === "Excellent" ? 5 : 
                      formData.criteria?.time === "Very Satisfactory" ? 4 :
                      formData.criteria?.time === "Satisfactory" ? 3 :
                      formData.criteria?.time === "Fair" ? 2 : 1,
        culturalSensitivity: formData.criteria?.materials === "Excellent" ? 5 : 
                           formData.criteria?.materials === "Very Satisfactory" ? 4 :
                           formData.criteria?.materials === "Satisfactory" ? 3 :
                           formData.criteria?.materials === "Fair" ? 2 : 1,
        demographics: {
          age: formData.age || "",
          gender: formData.gender || "",
          location: formData.location || ""
        },
        participationFrequency: formData.participationFrequency || "First time",
        additionalComments: formData.comment || ""
      };

      // Submit to analytics service
      await evaluationAnalyticsService.submitBeneficiaryEvaluation(
        (selectedEvent?.id ?? eventId).toString(),
        selectedEvent?.eventType ?? eventType,
        beneficiaryData,
        startTimeRef.current,
        selectedEvent
          ? {
              durationEnd: selectedEvent.durationEnd,
            }
          : undefined
      );

      // Call custom onSubmit if provided
      if (onSubmit) {
        onSubmit(beneficiaryData);
      } else {
        // Show success message
        alert('Beneficiary evaluation submitted successfully! Thank you for your feedback.');
        
        // Close the form
        handleClose();
      }
      
    } catch (error) {
      console.error('Error submitting beneficiary evaluation:', error);
      const errorMessage =
        (error as Error)?.message ||
        "There was an error submitting your evaluation. Please try again.";
      showSnackbarMessage(errorMessage, "error");
    } finally {
      setIsLoading(false);
    }
  };

  const formContent = (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Select the service or program you participated in
        </Typography>
        <FlexBox gap="20px" flexWrap="wrap">
          <CustomDropdown
            label="Select Finished Event (Available for 1 week after event ends)"
            width="100%"
            disabled={isLoadingEvents || availableEvents.length === 0}
            initialValue={selectedEventId ?? ""}
            menu={availableEvents.map((option) => {
              const end = dayjs(option.durationEnd);
              const now = dayjs();
              const daysSinceEnd = now.diff(end, 'day', true);
              const daysRemaining = Math.max(0, Math.ceil(7 - daysSinceEnd));
              const label = `${option.title} • Ended ${end.format(
                "MMM D, YYYY h:mm A"
              )}${daysRemaining > 0 ? ` • ${daysRemaining} day(s) remaining` : ''}`;
              return {
                key: label,
                value: option.id.toString(),
              };
            })}
            onChange={(event) => {
              setSelectedEventId(event.target.value);
            }}
          />
        </FlexBox>
        {availableEvents.length === 0 && !isLoadingEvents && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 1 }}
          >
            There are no finished events available for evaluation at this time.
          </Typography>
        )}
      </Box>

      {selectedEvent && evaluationWindowSummary && (
        <Box
          sx={{
            borderRadius: "12px",
            backgroundColor: "#f7f3e6",
            border: "1px solid rgba(192, 127, 0, 0.3)",
            p: 2,
          }}
        >
          <Typography variant="subtitle1" fontWeight="bold">
            Selected Event Details
          </Typography>
          <Typography variant="body2">
            <strong>Title:</strong> {selectedEvent.title}
          </Typography>
          <Typography variant="body2">
            <strong>Duration:</strong>{" "}
            {`${dayjs(selectedEvent.durationStart).format(
              "MMMM D, YYYY h:mm A"
            )} - ${evaluationWindowSummary.end}`}
          </Typography>
          <Typography variant="body2">
            <strong>Location:</strong>{" "}
            {selectedEvent.venue || selectedEvent.location || "TBA"}
          </Typography>
        </Box>
      )}

      <BeneficiariesRawEvalForm
        eventData={
          selectedEvent
            ? {
                title: selectedEvent.title,
                date: `${dayjs(selectedEvent.durationStart).format(
                  "MMMM D, YYYY h:mm A"
                )} - ${dayjs(selectedEvent.durationEnd).format(
                  "MMMM D, YYYY h:mm A"
                )}`,
                venue: selectedEvent.venue || selectedEvent.location || "TBA",
              }
            : eventData
        }
      />
    </Box>
  );

  return (
    <BaseEvaluationForm
      open={open}
      onClose={handleClose}
      title="Beneficiary Evaluation Form"
      subtitle="Help us improve our community services"
      formContent={formContent}
      onSubmit={handleSubmit}
      submitButtonText="Submit Beneficiary Evaluation"
      isLoading={isLoading}
    />
  );
};

export default BeneficiariesEvaluationForm;
