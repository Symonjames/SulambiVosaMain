import { Typography, TypographyProps } from "@mui/material";
import { useMediaQuery } from "react-responsive";

const TextHeader: React.FC<TypographyProps> = (props) => {
  const isMobile = useMediaQuery({
    query: "(max-width: 600px)",
  });

  return (
    <Typography
      {...props}
      variant={isMobile ? "h6" : "h5"}
      fontWeight="bold"
      color="var(--text-landing)"
    />
  );
};

export default TextHeader;
