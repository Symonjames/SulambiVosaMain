import CustomButton from "../Buttons/CustomButton";
import LoginIcon from "@mui/icons-material/Login";
import PersonAddAltIcon from "@mui/icons-material/PersonAddAlt";
import LineButton from "../Buttons/LineButton";
import FlexBox from "../FlexBox";
import { useNavigate } from "react-router-dom";
import { useContext } from "react";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { useMediaQuery } from "react-responsive";

interface Props {
  setOpenMembership?: (state: boolean) => void;
}

const LandingHeader = ({ setOpenMembership }: Props) => {
  const navigator = useNavigate();
  const { setFormData } = useContext(FormDataContext);

  const isMobile = useMediaQuery({
    query: "(max-width: 1224px)",
  });

  return (
    <>
      <header className={isMobile ? "headerMobile" : ""}>
        <FlexBox justifyContent="space-between" marginRight="20px" gap="50px">
          <LineButton
            label="Home"
            active
            style={{ fontSize: isMobile ? "10.5pt" : "" }}
          />
          <LineButton
            label="Events"
            onClick={() => {
              window.location.href = "#events";
            }}
            style={{ fontSize: isMobile ? "10.5pt" : "" }}
          />
        </FlexBox>
        {!isMobile ? (
          <>
            <CustomButton
              disableElevation
              variant="outlined"
              label="Be a member"
              endIcon={<PersonAddAltIcon />}
              sx={{ border: "2px solid white" }}
              hoverSx={{
                backgroundColor: "white",
                color: "black",
              }}
              onClick={() => {
                setFormData({});
                setOpenMembership && setOpenMembership(true);
              }}
            />
            <CustomButton
              disableElevation
              variant="contained"
              label="Sign In"
              endIcon={<LoginIcon />}
              onClick={() => {
                navigator("/login");
              }}
            />
          </>
        ) : (
          <>
            <LineButton
              label="Be a member"
              style={{ fontSize: "10.5pt" }}
              onClick={() => {
                setFormData({});
                setOpenMembership && setOpenMembership(true);
              }}
            />
            <LineButton
              label="Sign In"
              onClick={() => {
                navigator("/login");
              }}
              style={{ fontSize: isMobile ? "10.5pt" : "" }}
            />
          </>
        )}
      </header>
    </>
  );
};

export default LandingHeader;
