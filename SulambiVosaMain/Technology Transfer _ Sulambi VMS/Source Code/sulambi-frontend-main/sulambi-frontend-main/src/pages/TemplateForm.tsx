import { Box } from "@mui/material";
import { useRef } from "react";
import FlexBox from "../components/FlexBox";
import EvaluationForm from "../components/TemplateForms/TemplateForms/EvaluationForm";
import { useZoomTracker } from "../utils/printFormBorderLogger";

const TemplateForm = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Enable border logging for debugging
  useZoomTracker(containerRef, true);

  return (
    <FlexBox
      width="100%"
      height="100%"
      justifyContent="center"
      alignItems="center"
    >
      <Box 
        ref={containerRef}
        height="13in" 
        width="8.5in" 
        boxShadow="0 0 12px 1px gray"
      >
        <EvaluationForm />
      </Box>
    </FlexBox>
  );
};

export default TemplateForm;
