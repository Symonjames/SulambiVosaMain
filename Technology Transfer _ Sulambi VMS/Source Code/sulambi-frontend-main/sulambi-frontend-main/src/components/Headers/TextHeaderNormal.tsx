import { Typography, TypographyProps } from "@mui/material";

const TextHeaderNormal: React.FC<TypographyProps> = (props) => {
  return (
    <Typography
      {...props}
      variant="h6"
      fontWeight="bold"
      color="var(--text-default)"
    />
  );
};

export default TextHeaderNormal;
