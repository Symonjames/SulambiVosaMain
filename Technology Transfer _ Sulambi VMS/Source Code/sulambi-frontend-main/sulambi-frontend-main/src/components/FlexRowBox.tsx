import { BoxProps } from "@mui/material";
import FlexBox from "./FlexBox";

const FlexRowBox: React.FC<BoxProps> = (props) => {
  return (
    <FlexBox 
      {...props} 
      width="100%" 
      gap="10px" 
      flexDirection="row"
      alignItems="stretch"
    >
      {props.children}
    </FlexBox>
  );
};

export default FlexRowBox;
