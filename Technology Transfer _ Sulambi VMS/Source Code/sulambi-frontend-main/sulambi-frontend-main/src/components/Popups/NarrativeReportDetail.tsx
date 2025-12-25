import { Box, Typography } from "@mui/material";
import PopupModal from "../Modal/PopupModal";
import CustomDivider from "../Divider/CustomDivider";
import dayjs from "dayjs";
import { ExternalReportType, InternalReportType } from "../../interface/types";

interface Props {
  open: boolean;
  setOpen?: (state: boolean) => void;
  reportData: ExternalReportType | InternalReportType | null;
  reportType: "external" | "internal";
}

const NarrativeReportDetail: React.FC<Props> = (props) => {
  const { open, reportData, reportType, setOpen } = props;

  if (!reportData) return null;

  const event = reportData.eventId;

  return (
    <PopupModal
      open={open}
      setOpen={setOpen}
      header="Narrative Report Details"
      maxWidth="60vh"
    >
      <Box marginTop="20px">
        <Typography>
          <b>Event Title: </b>
          {event?.title || "N/A"}
        </Typography>
        <Typography>
          <b>Event Date: </b>{" "}
          {event?.durationStart && event?.durationEnd
            ? `${dayjs(event.durationStart).format("MMMM D, YYYY h:mm A")} - ${dayjs(event.durationEnd).format("MMMM D, YYYY h:mm A")}`
            : "N/A"}
        </Typography>
        <Typography>
          <b>Location: </b>
          {reportType === "external"
            ? (event as any)?.location || "N/A"
            : (event as any)?.venue || "N/A"}
        </Typography>
        <Typography>
          <b>Beneficiaries: </b>{" "}
          {(event as any)?.beneficiaries ??
            (event as any)?.participant ??
            "N/A"}
        </Typography>
        <Typography>
          <b>Description: </b> {event?.description || "N/A"}
        </Typography>
        <br />
        <CustomDivider />
        <br />
        
        {/* Narrative Report Section */}
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          Narrative Report
        </Typography>
        <Box 
          sx={{
            maxHeight: "300px",
            overflowY: "auto",
            padding: "12px",
            backgroundColor: "#f9f9f9",
            borderRadius: "8px",
            border: "1px solid #e0e0e0",
            marginBottom: "16px"
          }}
        >
          <Typography 
            component="div"
            dangerouslySetInnerHTML={{ __html: reportData.narrative || "No narrative report available." }}
          />
        </Box>

        {/* Photos Section */}
        {reportData.photos && reportData.photos.length > 0 && (
          <>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Event Photos ({reportData.photos.length})
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Photos are available in the full report view.
            </Typography>
          </>
        )}

        {/* Financial Information for Internal Reports */}
        {reportType === "internal" && (reportData as InternalReportType).finance && (
          <>
            <br />
            <CustomDivider />
            <br />
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Financial Information
            </Typography>
            <Typography>
              <b>Budget Utilized: </b>
              ₱{(reportData as InternalReportType).finance.budgetUtilized?.toLocaleString() || "0"}
            </Typography>
            <Typography>
              <b>Budget Source: </b>
              {(reportData as InternalReportType).finance.budgetUtilizedSource || "N/A"}
            </Typography>
            <Typography>
              <b>PS Attribution: </b>
              ₱{(reportData as InternalReportType).finance.psAttribution?.toLocaleString() || "0"}
            </Typography>
            <Typography>
              <b>PS Attribution Source: </b>
              {(reportData as InternalReportType).finance.psAttributionSource || "N/A"}
            </Typography>
          </>
        )}
      </Box>
    </PopupModal>
  );
};

export default NarrativeReportDetail;









































