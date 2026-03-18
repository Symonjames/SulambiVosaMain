import { Divider } from "@mui/material";
import { CustomDividerProps } from "../../interface/props";

const CustomDivider: React.FC<CustomDividerProps> = (props) => {
  return (
    <Divider
      {...props}
      sx={{
        width: props.width,
        margin: "auto",
        marginTop: props.mt,
        marginBottom: props.mb,
        borderBottom:
          props.thickness && props.color
            ? `${props.thickness} solid ${props.color}`
            : "",
      }}
    />
  );
};

export default CustomDivider;
