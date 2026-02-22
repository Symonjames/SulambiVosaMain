import React, { useState, useRef, useMemo, useEffect } from "react";
import { useContext } from "react";
import BaseEvaluationForm from "./BaseEvaluationForm";
import BeneficiariesRawEvalForm from "./raw/BeneficiariesRawEvalForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { evaluationAnalyticsService, BeneficiaryEvaluationData } from "../../services/evaluationAnalytics";
import dayjs from "dayjs";
import { Box, Typography } from "@mui/material";
import CustomDropdown from "../Inputs/CustomDropdown";
import CustomInput from "../Inputs/CustomInput";
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
  requiresBeneficiaryPin?: boolean;
}

type Step = 'pin' | 'survey';

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
  const [eventPin, setEventPin] = useState("");
  const [step, setStep] = useState<Step>('pin');

  useEffect(() => {
    if (open) {
      startTimeRef.current = Date.now();
      setStep('pin');
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
    setEventPin("");
    setStep('pin');
    if (setOpen) {
      setOpen(false);
    }
  };

  const handlePinContinue = async () => {
    const pin = (eventPin || "").trim();
    if (selectedEvent?.requiresBeneficiaryPin) {
      if (pin.length !== 5) {
        showSnackbarMessage(
          "Please enter the 5-digit event PIN to continue.",
          "warning"
        );
        return;
      }
      setIsLoading(true);
      try {
        await evaluationAnalyticsService.validateBeneficiaryPin(
          selectedEvent.id.toString(),
          selectedEvent.eventType ?? "external",
          pin
        );
        setStep("survey");
      } catch (err) {
        const msg = (err as Error)?.message ?? "Wrong PIN.";
        showSnackbarMessage(msg, "error");
      } finally {
        setIsLoading(false);
      }
      return;
    }
    setStep("survey");
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

      if (selectedEvent.requiresBeneficiaryPin) {
        const pin = (eventPin || "").trim();
        if (pin.length !== 5) {
          showSnackbarMessage(
            "This event requires a 5-digit event PIN. Please enter the PIN provided at the event.",
            "warning"
          );
          setIsLoading(false);
          return;
        }
      }

      // Require all questions to be answered (ratings + text questions) before submitting.
      const ratingLabels = [
        "Excellent",
        "Very Satisfactory",
        "Satisfactory",
        "Fair",
        "Poor",
      ] as const;
      const isValidRating = (v: unknown): v is (typeof ratingLabels)[number] =>
        typeof v === "string" && (ratingLabels as readonly string[]).includes(v);

      const criteria = (formData as any)?.criteria ?? {};
      const requiredRatingFields: Array<{ key: string; label: string }> = [
        { key: "overall", label: "Overall rating" },
        { key: "appropriateness", label: "Organization and support" },
        { key: "expectations", label: "Expectations communication" },
        { key: "session", label: "Meaningful and relevant activities" },
        { key: "time", label: "Time allocation" },
        { key: "materials", label: "Materials/resources adequacy" },
        { key: "relevance", label: "Coordinator knowledge and guidance" },
        { key: "explained", label: "Tasks/procedures explanation" },
        { key: "learningEnvironment", label: "Welcoming environment" },
        { key: "timeManagement", label: "Schedule management" },
        { key: "keenness", label: "Attentiveness to needs/concerns" },
        { key: "venue", label: "Venue suitability and safety" },
      ];

      const missing: string[] = [];
      for (const f of requiredRatingFields) {
        if (!isValidRating(criteria?.[f.key])) missing.push(f.label);
      }

      const requiredTextFields: Array<{ key: string; label: string }> = [
        { key: "q13", label: "Q13" },
        { key: "q14", label: "Q14" },
        { key: "comment", label: "Comments/commendations/complaints" },
        { key: "recommendations", label: "Recommendations" },
      ];
      for (const f of requiredTextFields) {
        const v = (formData as any)?.[f.key];
        if (!String(v ?? "").trim()) missing.push(f.label);
      }

      if (missing.length > 0) {
        showSnackbarMessage(
          `Please answer all questions before submitting. Missing: ${missing.join(", ")}.`,
          "warning"
        );
        setIsLoading(false);
        return;
      }

      const ratingToNumber = (rating: string): number => {
        switch (rating) {
          case "Excellent":
            return 5;
          case "Very Satisfactory":
            return 4;
          case "Satisfactory":
            return 3;
          case "Fair":
            return 2;
          default:
            return 1;
        }
      };

      // Extract form data and convert to BeneficiaryEvaluationData format
      const beneficiaryData: BeneficiaryEvaluationData = {
        overallSatisfaction: ratingToNumber(criteria.overall),
        serviceQuality: ratingToNumber(criteria.appropriateness),
        volunteerHelpfulness: ratingToNumber(criteria.expectations),
        impactOnCommunity: ratingToNumber(criteria.session),
        accessibility: ratingToNumber(criteria.time),
        culturalSensitivity: ratingToNumber(criteria.materials),
        demographics: {
          age: formData.age || "",
          gender: formData.gender || "",
          location: formData.location || ""
        },
        participationFrequency: formData.participationFrequency || "First time",
        additionalComments: String(formData.comment ?? ""),
        q13: String(formData.q13 ?? ""),
        q14: String(formData.q14 ?? ""),
        recommendations: String(formData.recommendations ?? "")
      };

      // Submit to analytics service (include PIN when event requires it)
      await evaluationAnalyticsService.submitBeneficiaryEvaluation(
        (selectedEvent?.id ?? eventId).toString(),
        selectedEvent?.eventType ?? eventType,
        beneficiaryData,
        startTimeRef.current,
        selectedEvent
          ? {
              durationEnd: selectedEvent.durationEnd,
            }
          : undefined,
        selectedEvent?.requiresBeneficiaryPin ? (eventPin || "").trim() : undefined
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

  const categorizedEvents = useMemo(() => {
    const now = dayjs();
    const nowMs = Date.now();
    const sevenDaysMs = 7 * 24 * 60 * 60 * 1000;
    const cutoffMs = nowMs - sevenDaysMs;

    const endMs = (option: EvaluationEventOption) => {
      const v = option.durationEnd;
      if (typeof v === "number") return v < 1e12 ? v * 1000 : v;
      return dayjs(v).valueOf();
    };

    const startMs = (option: EvaluationEventOption) => {
      const v = option.durationStart;
      if (typeof v === "number") return v < 1e12 ? v * 1000 : v;
      return dayjs(v).valueOf();
    };

    const ongoing: EvaluationEventOption[] = [];
    const endedWithin7Days: EvaluationEventOption[] = [];

    availableEvents.forEach((option) => {
      const end = endMs(option);
      const start = startMs(option);
      // Ongoing: started but not ended yet
      if (start <= nowMs && end > nowMs) {
        ongoing.push(option);
      } else if (end <= nowMs && end >= cutoffMs) {
        // Ended within 7 days
        endedWithin7Days.push(option);
      }
    });

    return { ongoing, endedWithin7Days };
  }, [availableEvents]);

  const allEventsMenu = useMemo(() => {
    const menu: { key: string; value: string }[] = [];
    
    // Add ongoing events first
    categorizedEvents.ongoing.forEach((option) => {
      const end = dayjs(option.durationEnd);
      const label = `[Ongoing] ${option.title} • Ends ${end.format("MMM D, YYYY h:mm A")}`;
      menu.push({
        key: label,
        value: option.id.toString(),
      });
    });

    // Add ended within 7 days events
    categorizedEvents.endedWithin7Days.forEach((option) => {
      const end = dayjs(option.durationEnd);
      const now = dayjs();
      const daysSinceEnd = now.diff(end, "day", true);
      const daysRemaining = Math.max(0, Math.ceil(7 - daysSinceEnd));
      const label = `[Ended] ${option.title} • Ended ${end.format("MMM D, YYYY h:mm A")}${daysRemaining > 0 ? ` • ${daysRemaining} day(s) remaining` : ""}`;
      menu.push({
        key: label,
        value: option.id.toString(),
      });
    });

    return menu;
  }, [categorizedEvents]);

  const pinStepContent = (
    <Box display="flex" flexDirection="column" gap={3}>
      {availableEvents.length > 1 && (
        <Box>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Select the event you participated in
          </Typography>
          <CustomDropdown
            label="Available Events"
            width="100%"
            disabled={isLoadingEvents || availableEvents.length === 0}
            initialValue={selectedEventId ?? ""}
            menu={allEventsMenu}
            onChange={(event) => setSelectedEventId(event.target.value)}
          />
        </Box>
      )}
      {selectedEvent && (
        <>
          <Box
            sx={{
              borderRadius: "12px",
              backgroundColor: "rgba(255,255,255,0.2)",
              border: "1px solid rgba(255,255,255,0.3)",
              p: 2,
            }}
          >
            <Typography variant="subtitle2" sx={{ opacity: 0.9 }} gutterBottom>
              You are about to evaluate
            </Typography>
            <CustomDropdown
              label="Select Event"
              width="100%"
              disabled={isLoadingEvents || availableEvents.length === 0}
              initialValue={selectedEventId ?? ""}
              menu={allEventsMenu}
              onChange={(event) => setSelectedEventId(event.target.value)}
            />
          </Box>
          <Box>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Event PIN
            </Typography>
            <Typography variant="body2" sx={{ mb: 1, opacity: 0.95 }}>
              Enter the 5-digit PIN that was shared at the event to continue.
            </Typography>
            <CustomInput
              label="Event PIN (5 digits)"
              value={eventPin}
              onChange={(e) => setEventPin((e.target.value || "").replace(/\D/g, "").slice(0, 5))}
              size="small"
              fullWidth
              placeholder="5 digits"
              inputProps={{ maxLength: 5, inputMode: "numeric" }}
            />
          </Box>
        </>
      )}
      {availableEvents.length === 0 && !isLoadingEvents && (
        <Typography variant="body2" color="text.secondary">
          There are no finished events available for evaluation at this time.
        </Typography>
      )}
    </Box>
  );

  const surveyFormContent = (
    <Box display="flex" flexDirection="column" gap={3}>
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
            Evaluating
          </Typography>
          <Typography variant="body2">
            <strong>{selectedEvent.title}</strong>
          </Typography>
          <Typography variant="body2">
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
      title={step === 'pin' ? 'Enter Event PIN' : 'Beneficiary Evaluation Form'}
      subtitle={step === 'pin' ? 'Enter the PIN provided at the event to continue' : 'Help us improve our community services'}
      formContent={step === 'pin' ? pinStepContent : surveyFormContent}
      onSubmit={step === 'pin' ? handlePinContinue : handleSubmit}
      submitButtonText={step === 'pin' ? 'Continue' : 'Submit Beneficiary Evaluation'}
      isLoading={isLoading}
    />
  );
};

export default BeneficiariesEvaluationForm;
