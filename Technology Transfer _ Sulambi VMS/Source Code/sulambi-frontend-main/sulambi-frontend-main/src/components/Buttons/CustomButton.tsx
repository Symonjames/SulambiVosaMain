import { Button } from "@mui/material";
import { CustomButtonProps } from "../../interface/props";

const CustomButton: React.FC<CustomButtonProps> = (props) => {
  const { hoverSx, hoverWhite, ...buttonProps } = props;
  
  return (
    <Button
      {...buttonProps}
      sx={{
        color: props.variant === "outlined" ? "white" : "var(--text-default)",
        bgcolor: props.variant === "contained" ? "white" : undefined,
        transition: "0.5s",
        textTransform: "none",
        ":hover": hoverWhite
          ? {
              bgcolor: "white",
              color: "black",
              ...hoverSx,
            }
          : {
              ...hoverSx,
            },
        ...props.sx,
      }}
    >
      {props.label}
    </Button>
  );
};

export default CustomButton;
