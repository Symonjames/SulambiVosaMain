import { Box, Typography, CircularProgress } from "@mui/material";
import PopupModal from "../Modal/PopupModal";
import CustomDivider from "../Divider/CustomDivider";
import { useEffect, useState } from "react";
import { getEventDetails } from "../../api/dashboard";
import {
  ExternalEventProposalType,
  InternalEventProposalType,
} from "../../interface/types";
import dayjs from "dayjs";
import SafeHtmlRenderer from "../Inputs/SafeHtmlRenderer";

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toDisplayText = (value: unknown): string => {
    if (value == null) return "N/A";
    const raw = String(value);
    if (!raw.trim()) return "N/A";

    // Convert rich-text HTML content (e.g. "<p>...</p>") to plain display text.
    const stripped = raw
      .replace(/<[^>]*>/g, " ")
      .replace(/&nbsp;/gi, " ")
      .replace(/\s+/g, " ")
      .trim();

    return stripped || "N/A";
  };

  useEffect(() => {
    if (!open) {
      setResponse(undefined);
      setError(null);
      return;
    }
    
    // Only fetch if we have valid eventId and eventType
    if (!eventId || !eventType) {
      setError("Invalid event ID or type");
      return;
    }

    setLoading(true);
    setError(null);
    getEventDetails(eventId, eventType)
      .then((response) => {
        const responseData: ResponseData = response.data.data;
        setResponse(responseData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching event details:", err);
        setError(err.response?.data?.message || "Failed to load event details");
        setLoading(false);
      });
  }, [open, eventId, eventType]);

  return (
    <PopupModal
      open={open}
      setOpen={setOpen}
      header="Event Details"
      maxWidth="60vh"
    >
      <Box marginTop="20px">
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : response?.event ? (
          <>
            <Typography>
              <b>Title: </b>
              {response.event.title || "N/A"}
            </Typography>
            <Typography>
              <b>Event Date : </b>{" "}
              {response.event.durationStart && response.event.durationEnd
                ? `${dayjs(response.event.durationStart).format("MMMM D, YYYY h:mm A")} - ${dayjs(response.event.durationEnd).format("MMMM D, YYYY h:mm A")}`
                : "N/A"}
            </Typography>
            <Typography>
              <b>Location : </b>
              {eventType === "external"
                ? (response.event as ExternalEventProposalType)?.location || "N/A"
                : (response.event as InternalEventProposalType)?.venue || "N/A"}
            </Typography>
            <Typography>
              <b>Beneficiaries : </b>{" "}
              {toDisplayText(
                (response.event as ExternalEventProposalType)?.beneficiaries ??
                  (response.event as InternalEventProposalType)?.participant
              )}
            </Typography>
            <Typography component="div">
              <b>Description : </b>{" "}
              {response.event.description != null && /<[^>]+>/.test(String(response.event.description)) ? (
                <SafeHtmlRenderer
                  htmlContent={String(response.event.description)}
                  style={{ marginTop: 4, display: "block" }}
                />
              ) : (
                response.event.description || "N/A"
              )}
            </Typography>
            <br />
            <CustomDivider />
            <br />
            <Typography>
              Total Number of Registered Participants for the Event:{" "}
              {response.registered ?? 0}
            </Typography>
            <Typography>
              Total Number of Attended Participants for the Event:{" "}
              {response.attended ?? 0}
            </Typography>
          </>
        ) : (
          <Typography>No event data available</Typography>
        )}
      </Box>
    </PopupModal>
  );
};

export default EventDetail;
