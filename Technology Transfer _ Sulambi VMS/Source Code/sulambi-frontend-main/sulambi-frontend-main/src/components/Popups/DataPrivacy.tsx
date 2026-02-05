import React from "react";
import PopupModal from "../Modal/PopupModal";
import { Typography } from "@mui/material";
import FlexBox from "../FlexBox";
import PrimaryButton from "../Buttons/PrimaryButton";

interface Props {
  open: boolean;
  setOpen?: (state: boolean) => void;
  onDecline?: () => void;
}

const DataPrivacy: React.FC<Props> = ({ open, onDecline, setOpen }) => {
  return (
    <PopupModal
      hideCloseButton
      open={open}
      setOpen={setOpen}
      header="Event Details"
      maxWidth="40vw"
      zval={10}
    >
      <Typography>
        By using this system, you agree to the collection and use of your
        personal data, including but not limited to your name, contact
        information (e.g., email address and phone number), address, and any
        other necessary details required for the system's operations. The
        purpose of collecting this information is strictly limited to
        facilitating system-related processes and services, verifying user
        identity and access, and monitoring and improving the system's
        functionality and efficiency. Your personal data will only be accessible
        to authorized system administrators who are tasked with managing and
        ensuring the proper operation of the system. The administrators are
        committed to maintaining the confidentiality and security of your data.
        Under no circumstances will your personal information be shared,
        disclosed, or used for purposes other than those explicitly stated
        without your consent, unless required by law. We take data privacy
        seriously and employ appropriate technical and organizational measures
        to protect your information against unauthorized access, loss, or
        breach. By agreeing to these terms, you acknowledge that while
        reasonable efforts are made to secure your data, no system can guarantee
        absolute security. However, any breach will be addressed promptly and
        transparently in compliance with applicable privacy laws.
      </Typography>
      <FlexBox justifyContent="flex-end" gap="20px">
        <PrimaryButton
          label="I Agree"
          onClick={() => {
            setOpen && setOpen(false);
          }}
        />
        <PrimaryButton
          label="Decline"
          onClick={() => {
            onDecline && onDecline();
            setOpen && setOpen(false);
          }}
        />
      </FlexBox>
    </PopupModal>
  );
};

export default DataPrivacy;
