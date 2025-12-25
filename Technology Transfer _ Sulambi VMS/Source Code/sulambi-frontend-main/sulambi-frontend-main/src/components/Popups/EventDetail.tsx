import { Box, Typography } from "@mui/material";
import PopupModal from "../Modal/PopupModal";
import CustomDivider from "../Divider/CustomDivider";
import { useEffect, useState } from "react";
import { getEventDetails } from "../../api/dashboard";
import {
  ExternalEventProposalType,
  InternalEventProposalType,
} from "../../interface/types";
import dayjs from "dayjs";

interface ResponseData {
  event: ExternalEventProposalType | InternalEventProposalType;
  registered: number;
  attended: number;
}

interface Props {
  open: boolean;
  setOpen?: (state: boolean) => void;
  eventId: number;
  eventType: "external" | "internal";
}

const EventDetail: React.FC<Props> = (props) => {
  const { open, eventId, eventType, setOpen } = props;
  const [response, setResponse] = useState<ResponseData>();

  useEffect(() => {
    if (!open) return setResponse(undefined);
    getEventDetails(eventId, eventType).then((response) => {
      const responseData: ResponseData = response.data.data;
      setResponse(responseData);
    });
  }, [open]);

  return (
    <PopupModal
      open={open}
      setOpen={setOpen}
      header="Event Details"
      maxWidth="60vh"
    >
      <Box marginTop="20px">
        <Typography>
          <b>Title: </b>
          {response?.event?.title}
        </Typography>
        <Typography>
          <b>Event Date : </b>{" "}
          {dayjs(response?.event?.durationStart).format("MMMM D, YYYY h:mm A")}{" "}
          - {dayjs(response?.event?.durationEnd).format("MMMM D, YYYY h:mm A")}
        </Typography>
        <Typography>
          <b>Location : </b>
          {eventType === "external"
            ? (response?.event as ExternalEventProposalType)?.location
            : (response?.event as InternalEventProposalType)?.venue}
        </Typography>
        <Typography>
          <b>Beneficiaries : </b>{" "}
          {(response?.event as ExternalEventProposalType)?.beneficiaries ??
            (response?.event as InternalEventProposalType)?.participant ??
            ""}
        </Typography>
        <Typography>
          <b>Description : </b> {response?.event.description}
        </Typography>
        <br />
        <CustomDivider />
        <br />
        <Typography>
          Total Number of Registered Participants for the Event:{" "}
          {response?.registered ?? 0}
        </Typography>
        <Typography>
          Total Number of Attended Participants for the Event:{" "}
          {response?.attended ?? 0}
        </Typography>
      </Box>
    </PopupModal>
  );
};

export default EventDetail;
