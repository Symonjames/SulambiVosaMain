import { Typography } from "@mui/material";
import PopupModal from "./PopupModal";
import FlexBox from "../FlexBox";
import PrimaryButton from "../Buttons/PrimaryButton";
import CustomDivider from "../Divider/CustomDivider";
import { ConfirmModalProps } from "../../interface/props";

const ConfirmModal: React.FC<ConfirmModalProps> = ({
  message,
  acceptText,
  declineText,
  title,
  onAccept,
  onCancel,
  open,
  zindex,
  setOpen,
}) => {
  return (
    <PopupModal
      header={title ?? "Membership application"}
      smallHeader
      minWidth="30vw"
      open={open}
      setOpen={setOpen}
      zval={zindex}
    >
      <CustomDivider width="100%" />
      <FlexBox marginTop="20px" justifyContent="center">
        <Typography gutterBottom textAlign="center">
          {message}
        </Typography>
      </FlexBox>
      <FlexBox
        justifyContent="flex-end"
        gap="10px"
        width="100%"
        marginTop="20px"
      >
        <PrimaryButton
          label={acceptText ?? "Yes"}
          sx={{ width: "50%" }}
          onClick={() => {
            onAccept && onAccept();
            setOpen && setOpen(false);
          }}
        />
        <PrimaryButton
          label={declineText ?? "Maybe Later"}
          sx={{ width: "50%", backgroundColor: "var(--button-red)" }}
          onClick={() => {
            onCancel && onCancel();
            setOpen && setOpen(false);
          }}
        />
      </FlexBox>
    </PopupModal>
  );
};

export default ConfirmModal;
