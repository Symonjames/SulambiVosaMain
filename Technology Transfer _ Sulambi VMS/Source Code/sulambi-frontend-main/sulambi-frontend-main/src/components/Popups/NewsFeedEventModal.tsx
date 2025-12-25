import { Box, Typography } from "@mui/material";
import PopupModal from "../Modal/PopupModal";
import CustomDivider from "../Divider/CustomDivider";
import dayjs from "dayjs";
import { ExternalReportType, InternalReportType } from "../../interface/types";
import { useMediaQuery } from "react-responsive";

const getBaseUrl = (): string => {
  const apiUri = (import.meta as any).env.VITE_API_URI as string | undefined;
  if (apiUri) return apiUri.replace("/api", "");
  if ((import.meta as any).env.DEV) return "http://localhost:8000";
  return window.location.origin;
};
const BASE_URL = getBaseUrl();

const buildImageUrl = (filename?: string) => {
  if (!filename) return "";
  let clean = filename.trim();
  try { clean = decodeURIComponent(clean); } catch {}
  clean = clean.replace(/\\/g, "/");
  clean = clean.replace(/^uploads[\/\\]/, "");
  return `${BASE_URL}/uploads/${clean}?t=${Date.now()}`;
};

interface Props {
  open: boolean;
  setOpen?: (state: boolean) => void;
  reportData: ExternalReportType | InternalReportType | null;
  reportType: "external" | "internal";
}

const NewsFeedEventModal: React.FC<Props> = (props) => {
  const { open, reportData, reportType, setOpen } = props;
  const isMobile = useMediaQuery({ query: "(max-width: 600px)" });

  if (!reportData) return null;

  const event = reportData.eventId;
  const photos = reportData.photos || [];
  const photoCaptions = reportData.photoCaptions || [];

  return (
    <PopupModal
      open={open}
      setOpen={setOpen}
      header="Event Report Details"
      maxWidth={isMobile ? "95vw" : "85vw"}
      maxHeight="90vh"
    >
      <Box sx={{ 
        maxHeight: "80vh", 
        overflowY: "auto",
        "&::-webkit-scrollbar": {
          width: "8px",
        },
        "&::-webkit-scrollbar-track": {
          background: "#f1f1f1",
          borderRadius: "4px",
        },
        "&::-webkit-scrollbar-thumb": {
          background: "#c1c1c1",
          borderRadius: "4px",
        },
        "&::-webkit-scrollbar-thumb:hover": {
          background: "#a8a8a8",
        },
      }}>
        {/* Photo 1 with Caption */}
        {photos.length > 0 && (
          <Box sx={{ marginBottom: "24px" }}>
            <img
              src={buildImageUrl(photos[0])}
              alt="Event photo"
              style={{
                width: "100%",
                height: "450px",
                objectFit: "cover",
                backgroundColor: "#f5f5f5",
                borderRadius: "8px"
              }}
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5YTNhZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlPC90ZXh0Pjwvc3ZnPg==';
              }}
            />
            {photoCaptions[0] && (
              <Typography 
                variant="body2" 
                sx={{ 
                  color: "rgba(0, 0, 0, 0.6)",
                  fontSize: "0.875rem",
                  lineHeight: 1.4,
                  fontStyle: "italic",
                  marginTop: "8px",
                  textAlign: "center"
                }}
              >
                {photoCaptions[0]}
              </Typography>
            )}
          </Box>
        )}

        {/* Narrative Report - No Title */}
        <Typography 
          component="div"
          variant="body1"
          sx={{ 
            lineHeight: 1.6,
            color: "#333"
          }}
          dangerouslySetInnerHTML={{ 
            __html: reportData.narrative || "No narrative report available." 
          }}
        />
      </Box>
    </PopupModal>
  );
};

export default NewsFeedEventModal;

