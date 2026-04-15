import React, { useState, useRef } from "react";
import { useContext } from "react";
import BaseEvaluationForm from "./BaseEvaluationForm";
import VolunteerRawEvalForm from "./raw/VolunteerRawEvalForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { evaluationAnalyticsService, VolunteerEvaluationData } from "../../services/evaluationAnalytics";
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
  onSubmit?: (data: VolunteerEvaluationData) => void;
}

const VolunteerEvaluationForm: React.FC<Props> = ({ 
  open,
  setOpen,
  eventId = "1",
  eventType = "external",
  eventData,
  onSubmit,
}: Props) => {
  const { formData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const [isLoading, setIsLoading] = useState(false);
  const startTimeRef = useRef<number>(Date.now());

  const handleClose = () => {
    if (setOpen) {
      setOpen(false);
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    
    try {
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

      const payloadCriteria: Record<string, string> = {
        overall: criteria.overall,
        appropriateness: criteria.appropriateness,
        expectations: criteria.expectations,
        session: criteria.session,
        time: criteria.time,
        materials: criteria.materials,
        venue: criteria.venue,
      };

      // Extract form data and convert to VolunteerEvaluationData format
      const volunteerData: VolunteerEvaluationData = {
        overallSatisfaction: formData.criteria?.overall === "Excellent" ? 5 : 
                           formData.criteria?.overall === "Very Satisfactory" ? 4 :
                           formData.criteria?.overall === "Satisfactory" ? 3 :
                           formData.criteria?.overall === "Fair" ? 2 : 1,
        eventOrganization: formData.criteria?.appropriateness === "Excellent" ? 5 : 
                          formData.criteria?.appropriateness === "Very Satisfactory" ? 4 :
                          formData.criteria?.appropriateness === "Satisfactory" ? 3 :
                          formData.criteria?.appropriateness === "Fair" ? 2 : 1,
        communication: formData.criteria?.expectations === "Excellent" ? 5 : 
                      formData.criteria?.expectations === "Very Satisfactory" ? 4 :
                      formData.criteria?.expectations === "Satisfactory" ? 3 :
                      formData.criteria?.expectations === "Fair" ? 2 : 1,
        supportProvided: formData.criteria?.materials === "Excellent" ? 5 : 
                        formData.criteria?.materials === "Very Satisfactory" ? 4 :
                        formData.criteria?.materials === "Satisfactory" ? 3 :
                        formData.criteria?.materials === "Fair" ? 2 : 1,
        learningExperience: formData.criteria?.session === "Excellent" ? 5 : 
                           formData.criteria?.session === "Very Satisfactory" ? 4 :
                           formData.criteria?.session === "Satisfactory" ? 3 :
                           formData.criteria?.session === "Fair" ? 2 : 1,
        participationLevel: formData.criteria?.learningEnvironment || "Moderate",
        skillDevelopment: formData.q13 || "",
        teamCollaboration: formData.criteria?.explained || "Good",
        challenges: formData.q14 || "",
        improvements: formData.comment || "",
        additionalComments: formData.recommendations || ""
      };

      // Submit to analytics service
      await evaluationAnalyticsService.submitVolunteerEvaluation(
        eventId,
        eventType,
        volunteerData,
        startTimeRef.current,
        {
          criteria: payloadCriteria,
          q13: String(formData.q13 ?? ""),
          q14: String(formData.q14 ?? ""),
          comment: String(formData.comment ?? ""),
          recommendations: String(formData.recommendations ?? ""),
        }
      );

      onSubmit?.(volunteerData);

      // Show success message
      alert('Volunteer evaluation submitted successfully! Thank you for your feedback.');
      
      // Close the form
      handleClose();
      
    } catch (error) {
      console.error('Error submitting volunteer evaluation:', error);
      alert('There was an error submitting your evaluation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <BaseEvaluationForm
      open={open}
      onClose={handleClose}
      title="Training / Seminar Evaluation Form"
      subtitle="Help us improve our training and seminar programs"
      formContent={<VolunteerRawEvalForm eventData={eventData} />}
      onSubmit={handleSubmit}
      submitButtonText="Submit Training Evaluation"
      isLoading={isLoading}
    />
  );
};

export default VolunteerEvaluationForm;

