import { IconButton } from "@mui/material";
import FlexBox from "../components/FlexBox";
import TextHeader from "../components/Headers/TextHeader";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import TextSubHeader from "../components/Headers/TextSubHeader";
import { useNavigate } from "react-router-dom";

interface ThankYouPageProps {
  mainMessage: string;
  subMessage?: string;
}

const ThankYouPage: React.FC<ThankYouPageProps> = ({
  mainMessage,
  subMessage,
}) => {
  const navigate = useNavigate();

  return (
    <FlexBox
      minHeight="100vh"
      width="100%"
      justifyContent="center"
      alignItems="center"
      flexDirection="column"
      bgcolor="white"
      sx={{
        background: "linear-gradient(180deg, #c07f00 0%, #ffdf75 100%)",
      }}
    >
      <>
        <IconButton
          sx={{ position: "fixed", top: "20px", left: "20px" }}
          onClick={() => navigate("/")}
        >
          <ArrowBackIcon />
        </IconButton>

        <TextHeader
          sx={{ fontSize: "30pt", fontWeight: "bold" }}
          textAlign={"center"}
        >
          {mainMessage}
        </TextHeader>
        <TextSubHeader sx={{ color: "black" }} textAlign={"center"}>
          {subMessage}
        </TextSubHeader>
      </>
    </FlexBox>
  );
};

export default ThankYouPage;
