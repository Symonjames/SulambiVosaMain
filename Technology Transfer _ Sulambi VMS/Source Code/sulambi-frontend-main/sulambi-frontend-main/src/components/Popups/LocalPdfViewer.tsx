import { useState, useEffect } from "react";
import { Document, Page, pdfjs } from "react-pdf";
// Import worker config for side effects (sets up worker before use)
import "../../utils/pdfjsWorker";
import { Box, IconButton, Typography, CircularProgress, Alert, Button } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import ZoomOutIcon from "@mui/icons-material/ZoomOut";
import DownloadIcon from "@mui/icons-material/Download";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

// PDF.js worker is configured in utils/pdfjsWorker.ts
// This ensures it's set before any react-pdf components are used

interface Props {
  url: string;
  open: boolean;
  setOpen?: (state: boolean) => void;
}

const LocalPDFViewer: React.FC<Props> = ({ url, open, setOpen }) => {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Worker is configured in utils/pdfjsWorker.ts (same-origin /pdf.worker.min.mjs)

  useEffect(() => {
    if (!open || !url) return;

    const fetchPdfData = async () => {
      setLoading(true);
      setError(null);
      setPageNumber(1);
      setPdfUrl(null);

      try {
        // Check if URL is a Cloudinary URL (public, no auth needed)
        const isCloudinaryUrl = url.includes("res.cloudinary.com") || url.includes("cloudinary.com");
        const isLocalUrl = url.startsWith("/uploads/") || url.includes("/uploads/") || url.startsWith("uploads/");
        
        const headers: HeadersInit = {};
        let fetchOptions: RequestInit = {
          headers,
        };
        
        // Auth via httpOnly cookie (credentials: include sends session_token cookie)
        if (!isCloudinaryUrl) {
          fetchOptions.credentials = "include";
        }
        // Request full file so we get a proper preview (avoid 206 Partial Content with 1 byte)
        if (isCloudinaryUrl) {
          (headers as Record<string, string>)["Range"] = "bytes=0-";
        }
        
        // For Cloudinary URLs, don't use credentials (they're public and cause CORS issues)
        // Cloudinary files are publicly accessible via URL
        
        // Fetch PDF (request full file for Cloudinary to avoid broken 206 partial response)
        let response = await fetch(url, fetchOptions);
        if (response.status === 416 && isCloudinaryUrl) {
          delete (headers as Record<string, string>)["Range"];
          response = await fetch(url, fetchOptions);
        }
        if (!response.ok) {
          if (response.status === 404 && isLocalUrl) {
            throw new Error(
              `File not found on server. This appears to be an old local file path. ` +
              `The file may have been moved or deleted. Please contact support if you need access to this file.`
            );
          }
          throw new Error(`Failed to load PDF: ${response.status} ${response.statusText}`);
        }

        const blob = await response.blob();
        const objectUrl = URL.createObjectURL(blob);
        setPdfUrl(objectUrl);
      } catch (err: any) {
        console.error("Error loading PDF:", err);
        setError(err.message || "Failed to load PDF. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchPdfData();

    // Cleanup object URL on unmount
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [url, open]);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setPageNumber(1);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error("PDF load error:", error);
    console.error("Error details:", error.message);
    console.error("Current worker source:", pdfjs.GlobalWorkerOptions.workerSrc);
    
    // Worker is served from same origin (/pdf.worker.min.mjs). If this still fails, suggest download.
    if (error.message.includes("worker") || 
        error.message.includes("Failed to fetch") || 
        error.message.includes("dynamically imported") ||
        error.message.includes("fake worker")) {
      setError(
        "PDF viewer worker failed to load. The PDF file is valid, but the viewer cannot initialize. " +
        "Please try downloading the file using the download button below, or refresh the page."
      );
    } else {
      const isCloudinary = url && (url.includes("res.cloudinary.com") || url.includes("cloudinary.com"));
      setError(
        isCloudinary
          ? "This file might not be a PDF (e.g. Word document). Click the download icon to open in a new tab."
          : "Failed to parse PDF. The file may be corrupted."
      );
      if (isCloudinary && url) {
        window.open(url, "_blank", "noopener,noreferrer");
      }
    }
    setLoading(false);
  };

  const goToPrevPage = () => {
    if (pageNumber > 1) {
      setPageNumber(pageNumber - 1);
    }
  };

  const goToNextPage = () => {
    if (numPages && pageNumber < numPages) {
      setPageNumber(pageNumber + 1);
    }
  };

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.25, 0.5));
  };

  const handleDownload = () => {
    if (pdfUrl) {
      const link = document.createElement("a");
      link.href = pdfUrl;
      link.download = url.split("/").pop() || "document.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleDownloadFallback = () => {
    // Prefer downloaded blob when available; otherwise open original source in a new tab.
    if (pdfUrl) {
      handleDownload();
      return;
    }
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  };

  if (!open) return null;

  return (
    <Box
      sx={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.9)",
        zIndex: 9999,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Header with controls */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          backgroundColor: "rgba(0, 0, 0, 0.95)",
          padding: "10px 20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          zIndex: 10001, // Higher than content
          boxShadow: "0 2px 10px rgba(0, 0, 0, 0.5)",
          minHeight: "60px",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton
            onClick={handleZoomOut}
            sx={{ color: "white" }}
            disabled={scale <= 0.5}
          >
            <ZoomOutIcon />
          </IconButton>
          <Typography sx={{ color: "white", minWidth: "60px", textAlign: "center" }}>
            {Math.round(scale * 100)}%
          </Typography>
          <IconButton
            onClick={handleZoomIn}
            sx={{ color: "white" }}
            disabled={scale >= 3}
          >
            <ZoomInIcon />
          </IconButton>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton
            onClick={goToPrevPage}
            sx={{ color: "white" }}
            disabled={pageNumber <= 1}
          >
            <NavigateBeforeIcon />
          </IconButton>
          <Typography sx={{ color: "white", minWidth: "100px", textAlign: "center" }}>
            Page {pageNumber} of {numPages || "?"}
          </Typography>
          <IconButton
            onClick={goToNextPage}
            sx={{ color: "white" }}
            disabled={!numPages || pageNumber >= numPages}
          >
            <NavigateNextIcon />
          </IconButton>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <IconButton onClick={handleDownload} sx={{ color: "white" }} title="Download PDF">
            <DownloadIcon />
          </IconButton>
          <IconButton
            onClick={() => setOpen && setOpen(false)}
            sx={{ color: "white" }}
            title="Close"
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </Box>

      {/* PDF Content - positioned below fixed header */}
      <Box
        sx={{
          position: "absolute",
          top: "70px", // Start below fixed header (header is ~60px + padding)
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          padding: "20px",
          overflow: "auto",
          zIndex: 1, // Below header (10001) but above background
        }}
      >
        {loading && (
          <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
            <CircularProgress sx={{ color: "white" }} />
            <Typography sx={{ color: "white" }}>Loading PDF...</Typography>
          </Box>
        )}

        {error && (
          <Box sx={{ maxWidth: "560px", width: "100%" }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Preview is unavailable for this file. Download if you want to see the contents.
            </Alert>
            <Box sx={{ display: "flex", justifyContent: "center" }}>
              <Button
                variant="contained"
                color="warning"
                startIcon={<DownloadIcon />}
                onClick={handleDownloadFallback}
              >
                Download File
              </Button>
            </Box>
          </Box>
        )}

        {pdfUrl && !loading && !error && (
          <Box
            sx={{
              backgroundColor: "white",
              padding: "20px",
              borderRadius: "4px",
              boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
              maxWidth: "100%",
              maxHeight: "calc(100vh - 120px)", // Account for header
              overflow: "auto",
            }}
          >
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <Box sx={{ display: "flex", justifyContent: "center", padding: "40px" }}>
                  <CircularProgress />
                </Box>
              }
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
            </Document>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default LocalPDFViewer;
