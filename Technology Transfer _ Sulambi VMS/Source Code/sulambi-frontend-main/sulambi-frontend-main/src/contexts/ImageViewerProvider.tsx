import { createContext, ReactNode, useState } from "react";
import LocalPdfViewer from "../components/Popups/LocalPdfViewer";
import LocalImageViewer from "../components/Popups/LocalImageViewer";
import { Box, IconButton, Typography } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

interface ImageDetails {
  source: string;
  type: "image" | "pdf" | "iframe";
}

interface GetSet {
  fileDetails: ImageDetails;
  openViewer?: boolean;
  setFileDetails: (imageDetails: ImageDetails) => void;
  setOpenViewer: (state: boolean) => void;
}

export const ImageViewerContext = createContext<GetSet>({
  fileDetails: { source: "", type: "image" },
  openViewer: false,
  setFileDetails: (imageDetails: ImageDetails) => {
    imageDetails;
  },
  setOpenViewer: (state: boolean) => {
    state;
  },
});

const ImageViewerProvider = ({ children }: { children: ReactNode }) => {
  const [openViewer, setOpenViewer] = useState(false);
  const [fileDetails, setFileDetails] = useState<ImageDetails>({
    source: "",
    type: "image",
  });

  return (
    <ImageViewerContext.Provider
      value={{
        fileDetails,
        openViewer,
        setFileDetails,
        setOpenViewer,
      }}
    >
      {fileDetails.type === "iframe" ? (
        openViewer && (
          <Box
            sx={{
              position: "fixed",
              inset: 0,
              zIndex: 10000,
              backgroundColor: "rgba(0,0,0,0.9)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              p: 2,
            }}
          >
            <Box
              sx={{
                backgroundColor: "#333",
                borderRadius: 1,
                maxWidth: 480,
                width: "100%",
                p: 2,
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                <Typography variant="subtitle1" color="white">Uploaded file</Typography>
                <IconButton size="small" onClick={() => setOpenViewer(false)} sx={{ color: "white" }}>
                  <CloseIcon />
                </IconButton>
              </Box>
              <Typography variant="body2" color="rgba(255,255,255,0.9)" sx={{ mb: 2 }}>
                This file cannot be previewed in the app. Copy the link or open it in a new tab (no automatic download).
              </Typography>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                <IconButton
                  size="small"
                  sx={{ color: "white", border: "1px solid rgba(255,255,255,0.5)", borderRadius: 1 }}
                  onClick={() => {
                    navigator.clipboard.writeText(fileDetails.source);
                    setOpenViewer(false);
                  }}
                >
                  Copy link
                </IconButton>
                <IconButton
                  size="small"
                  sx={{ color: "white", border: "1px solid rgba(255,255,255,0.5)", borderRadius: 1 }}
                  onClick={() => {
                    window.open(fileDetails.source, "_blank", "noopener,noreferrer");
                    setOpenViewer(false);
                  }}
                >
                  Open in new tab
                </IconButton>
              </Box>
            </Box>
          </Box>
        )
      ) : fileDetails.type === "image" ? (
        <LocalImageViewer
          open={openViewer}
          imageSource={fileDetails.source}
          setOpen={setOpenViewer}
        />
      ) : (
        <LocalPdfViewer
          url={fileDetails.source}
          open={openViewer}
          setOpen={setOpenViewer}
        />
      )}
      {children}
    </ImageViewerContext.Provider>
  );
};

export default ImageViewerProvider;
