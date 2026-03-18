import { Box, BoxProps } from "@mui/material";

const FlexBox: React.FC<BoxProps> = (props) => {
  return <Box display="flex" {...props} />;
};

export default FlexBox;
