import { Box, CircularProgress, Typography } from "@mui/material";
import FlexBox from "../FlexBox";

interface LoadingSpinnerProps {
  message?: string;
  size?: number;
  fullHeight?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = "Loading...",
  size = 60,
  fullHeight = true,
}) => {
  return (
    <FlexBox
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight={fullHeight ? "60vh" : "auto"}
      padding="40px"
    >
      <CircularProgress 
        size={size} 
        sx={{ 
          color: "var(--primary-color, #1976d2)",
          marginBottom: "20px"
        }} 
      />
      <Typography 
        variant="h6" 
        color="text.secondary"
        sx={{
          marginTop: "16px",
          fontWeight: 500,
          fontSize: "1.1rem"
        }}
      >
        {message}
      </Typography>
    </FlexBox>
  );
};

export default LoadingSpinner;

