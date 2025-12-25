import { Box } from "@mui/material";
import FlexBox from "../components/FlexBox";
import EvaluationForm from "../components/TemplateForms/TemplateForms/EvaluationForm";

const TemplateForm = () => {
  return (
    <FlexBox
      width="100%"
      height="100%"
      justifyContent="center"
      alignItems="center"
    >
      <Box height="13in" width="8.5in" boxShadow="0 0 12px 1px gray">
        <EvaluationForm />
      </Box>
    </FlexBox>
  );
};

export default TemplateForm;
