import { Box, Typography } from "@mui/material";
import PopupModal from "../Modal/PopupModal";
import CustomDivider from "../Divider/CustomDivider";
import dayjs from "dayjs";
import { ExternalReportType, InternalReportType } from "../../interface/types";
import {
  normalizePhotoList,
  resolveReportImageUrl,
} from "../../utils/uploadUrl";

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
  const internalReport = reportData as InternalReportType;

  const approvedBudget =
    internalReport.approvedBudget ?? internalReport.finance?.approvedBudget ?? 0;
  const approvedBudgetSource =
    internalReport.approvedBudgetSrc ?? internalReport.finance?.approvedBudgetSource ?? "N/A";
  const budgetUtilized =
    internalReport.budgetUtilized ?? internalReport.finance?.budgetUtilized ?? 0;
  const budgetUtilizedSource =
    internalReport.budgetUtilizedSrc ?? internalReport.finance?.budgetUtilizedSource ?? "N/A";
  const psAttribution =
    internalReport.psAttribution ?? internalReport.finance?.psAttribution ?? 0;
  const psAttributionSource =
    internalReport.psAttributionSrc ?? internalReport.finance?.psAttributionSource ?? "N/A";

  const formatCurrency = (value: number | string) => {
    const parsed = Number(value);
    const amount = Number.isFinite(parsed) ? parsed : 0;
    return `₱${amount.toLocaleString()}`;
  };

  const reportPhotos = normalizePhotoList((reportData as any)?.photos);

  const financialRows = [
    {
      itemDescription: "Approved Budget as Proposed",
      amount: approvedBudget,
      budgetSource: approvedBudgetSource,
    },
    {
      itemDescription: "Actual Budget Utilized",
      amount: budgetUtilized,
      budgetSource: budgetUtilizedSource,
    },
    {
      itemDescription: "Personal Services (PS) Attribution",
      amount: psAttribution,
      budgetSource: psAttributionSource,
    },
  ];

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

        {/* Photos Section — same URL rules as AdminPhotoDisplay / news carousel */}
        {reportPhotos.length > 0 && (
          <>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Event Photos ({reportPhotos.length})
            </Typography>
            <Box
              sx={{
                display: "flex",
                flexWrap: "wrap",
                gap: 2,
                mb: 2,
              }}
            >
              {reportPhotos.map((src, idx) => (
                <Box
                  key={`${src}-${idx}`}
                  component="img"
                  src={resolveReportImageUrl(src)}
                  alt={`Report photo ${idx + 1}`}
                  sx={{
                    maxWidth: { xs: "100%", sm: 280 },
                    maxHeight: 220,
                    objectFit: "cover",
                    borderRadius: 1,
                    border: "1px solid #e0e0e0",
                  }}
                />
              ))}
            </Box>
          </>
        )}

        {/* Financial Information for Internal Reports */}
        {reportType === "internal" && (
          <>
            <br />
            <CustomDivider />
            <br />
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Financial Information
            </Typography>
            <Box
              sx={{
                border: "1px solid #d0d0d0",
                borderRadius: "6px",
                overflow: "hidden",
                marginTop: "8px",
              }}
            >
              <Box sx={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", backgroundColor: "#f3f4f6", borderBottom: "1px solid #d0d0d0" }}>
                <Box sx={{ padding: "8px", fontWeight: 700, fontSize: "0.9rem" }}>Item Description</Box>
                <Box sx={{ padding: "8px", fontWeight: 700, fontSize: "0.9rem", borderLeft: "1px solid #d0d0d0" }}>Amount</Box>
                <Box sx={{ padding: "8px", fontWeight: 700, fontSize: "0.9rem", borderLeft: "1px solid #d0d0d0" }}>Budget Source</Box>
              </Box>
              {financialRows.map((row, index) => (
                <Box
                  key={row.itemDescription}
                  sx={{
                    display: "grid",
                    gridTemplateColumns: "2fr 1fr 1fr",
                    borderBottom: index < financialRows.length - 1 ? "1px solid #e5e7eb" : "none",
                  }}
                >
                  <Box sx={{ padding: "8px", fontSize: "0.9rem" }}>{row.itemDescription}</Box>
                  <Box sx={{ padding: "8px", fontSize: "0.9rem", borderLeft: "1px solid #e5e7eb" }}>{formatCurrency(row.amount)}</Box>
                  <Box sx={{ padding: "8px", fontSize: "0.9rem", borderLeft: "1px solid #e5e7eb" }}>{row.budgetSource || "N/A"}</Box>
                </Box>
              ))}
            </Box>
          </>
        )}
      </Box>
    </PopupModal>
  );
};

export default NarrativeReportDetail;









































