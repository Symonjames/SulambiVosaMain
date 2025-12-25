import React, { useState, useRef } from "react";
import { useContext } from "react";
import BaseEvaluationForm from "./BaseEvaluationForm";
import VolunteerRawEvalForm from "./raw/VolunteerRawEvalForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { evaluationAnalyticsService, VolunteerEvaluationData } from "../../services/evaluationAnalytics";

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
}

const VolunteerEvaluationForm: React.FC<Props> = ({ 
  open,
  setOpen,
  eventId = "1",
  eventType = "external",
  eventData
}: Props) => {
  const { formData } = useContext(FormDataContext);
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
        startTimeRef.current
      );

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

