import React from "react";
import CustomButton from "./CustomButton";
import { PrimaryButtomProps } from "../../interface/props";

const PrimaryButton: React.FC<PrimaryButtomProps> = ({
  label,
  icon,
  startIcon,
  sx,
  hoverSx,
  onClick,
}) => {
  return (
    <CustomButton
      label={label}
      variant="contained"
      endIcon={icon}
      startIcon={startIcon}
      onClick={onClick}
      sx={{
        backgroundColor: "var(--text-landing)",
        color: "white",
        ...sx,
      }}
      hoverSx={{
        color: "black",
        backgroundColor: "white",
        ...hoverSx,
      }}
    />
  );
};

export default PrimaryButton;
