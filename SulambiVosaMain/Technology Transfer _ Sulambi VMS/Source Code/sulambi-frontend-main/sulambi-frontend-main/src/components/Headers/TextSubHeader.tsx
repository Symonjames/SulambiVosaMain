import { Typography, TypographyProps } from "@mui/material";

const TextSubHeader: React.FC<TypographyProps> = (props) => {
  return <Typography {...props} color="var(--text-landing-light)" />;
};

export default TextSubHeader;
