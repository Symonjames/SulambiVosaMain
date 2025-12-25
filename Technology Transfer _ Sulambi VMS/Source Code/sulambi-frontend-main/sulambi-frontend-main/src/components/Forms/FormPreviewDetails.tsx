import React from "react";
import PopupModal from "../Modal/PopupModal";
import {
  ExternalEventProposalType,
  InternalEventProposalType,
} from "../../interface/types";
import { Typography, Box } from "@mui/material";
import dayjs from "dayjs";
import { useMediaQuery } from "react-responsive";
import SafeHtmlRenderer from "../Inputs/SafeHtmlRenderer";

interface Props {
  open: boolean;
  eventData: ExternalEventProposalType | InternalEventProposalType;
  setOpen?: (state: boolean) => void;
}

const FormPreviewDetails: React.FC<Props> = ({ open, eventData, setOpen }) => {
  const isMobile = useMediaQuery({
    query: "(max-width: 600px)",
  });

  return (
    <PopupModal
      open={open}
      setOpen={setOpen}
      header="Event Details"
      maxWidth={isMobile ? "95vw" : "40vw"}
    >
      <Typography>
        <b>Title:</b> {eventData.title}
      </Typography>
      <Typography>
        <b>Location:</b>{" "}
        {(eventData as ExternalEventProposalType).location ??
          (eventData as InternalEventProposalType)?.venue}
      </Typography>
      <Typography>
        <b>Duration:</b>{" "}
        {dayjs(eventData.durationStart).format("MMMM D, YYYY h:mm A") +
          " - " +
          dayjs(eventData.durationEnd).format("MMMM D, YYYY h:mm A")}
      </Typography>
      <Box mt={1}>
        <Typography component="div">
          <b>Description:</b>
        </Typography>
        <SafeHtmlRenderer
          htmlContent={eventData.description ?? ""}
          style={{ marginTop: "4px" }}
        />
      </Box>
    </PopupModal>
  );
};

export default FormPreviewDetails;
