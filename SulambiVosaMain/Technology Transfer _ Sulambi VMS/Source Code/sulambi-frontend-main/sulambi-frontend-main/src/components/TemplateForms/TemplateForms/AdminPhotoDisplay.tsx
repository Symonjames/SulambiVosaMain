import React, { useState, useEffect } from "react";
import { Box, Typography, styled } from "@mui/material";
import BrokenImageIcon from "@mui/icons-material/BrokenImage";
import SafeHtmlRenderer from "../../Inputs/SafeHtmlRenderer";

const BASE_API_URL = import.meta.env.VITE_API_URI ?? "http://localhost:8000/api";

const PhotoSectionWrapper = styled(Box)({
  width: "100%",
  maxWidth: "100%",
  overflow: "hidden",
  boxSizing: "border-box",
});

const PhotoGridContainer = styled(Box)({
  display: "flex",
  gap: "10px",
  width: "100%",
  padding: "6px",
  boxSizing: "border-box",
  justifyContent: "center",
  alignItems: "flex-start",
  "@media (max-width: 768px)": {
    flexDirection: "column",
    gap: "8px",
    padding: "4px",
  },
  "@media print": {
    display: "flex !important",
    flexDirection: "row !important",
    gap: "12px",
    padding: "6px",
    width: "100%",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
});

const PhotoItemContainer = styled("figure")({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: "6px",
  flex: "0 1 calc(50% - 6px)",
  minWidth: 0,
  maxWidth: "calc(50% - 6px)",
  boxSizing: "border-box",
  padding: "8px",
  margin: 0, // Reset default figure margin
  transition: "all 0.2s ease-in-out",
  "&:hover": {
    transform: "translateY(-2px)",
  },
  "@media (max-width: 768px)": {
    flex: "1 1 100%",
    maxWidth: "100%",
    padding: "6px",
  },
  "@media print": {
    display: "flex !important",
    flexDirection: "column !important",
    flex: "0 1 calc(50% - 6px) !important",
    maxWidth: "calc(50% - 6px) !important",
    minWidth: "calc(50% - 6px) !important",
    padding: "6px",
    margin: 0,
    gap: "6px",
    alignItems: "center",
    pageBreakInside: "avoid",
  },
});

const ImagePreviewContainer = styled(Box)({
  position: "relative",
  width: "100%",
  height: "100px",
  borderRadius: "6px",
  overflow: "hidden",
  backgroundColor: "#f8f9fa",
  boxSizing: "border-box",
  transition: "all 0.2s ease-in-out",
  "&:hover": {
    transform: "scale(1.02)",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
  },
  "@media print": {
    width: "100%",
    height: "100px",
    minHeight: "100px",
    maxHeight: "100px",
    borderRadius: "3px",
    backgroundColor: "#ffffff",
    border: "1px solid #e5e7eb",
    overflow: "hidden",
    boxSizing: "border-box",
  },
});

const StyledImage = styled("img")({
  width: "100%",
  height: "100%",
  objectFit: "cover",
  "@media print": {
    width: "100%",
    height: "100%",
    minHeight: "100px",
    maxHeight: "100px",
    objectFit: "cover",
    objectPosition: "center",
    display: "block",
  },
});

const FallbackContainer = styled(Box)({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "100%",
  backgroundColor: "#f5f5f5",
  color: "#666",
  gap: "8px",
});

const CaptionContainer = styled("figcaption")({
  width: "100%",
  minHeight: "32px",
  padding: "8px 12px",
  fontSize: "12px",
  color: "#374151",
  textAlign: "center",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  lineHeight: "1.3",
  fontWeight: "500",
  boxSizing: "border-box",
  wordWrap: "break-word",
  overflowWrap: "break-word",
  hyphens: "auto",
  margin: 0, // Reset default figcaption margin
  backgroundColor: "#f9fafb",
  border: "1px solid #e5e7eb",
  borderRadius: "6px",
  // Always show container, even when empty
  "@media print": {
    width: "100%",
    minHeight: "28px",
    padding: "6px 8px",
    fontSize: "10px",
    color: "#000000",
    textAlign: "center",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    lineHeight: "1.2",
    fontWeight: "400",
    boxSizing: "border-box",
    wordWrap: "break-word",
    overflowWrap: "break-word",
    hyphens: "auto",
    margin: 0,
    backgroundColor: "#ffffff",
    border: "1px solid #000000",
    borderRadius: "2px",
  },
});

interface PhotoData {
  filename: string;
  caption?: string;
}

interface AdminPhotoDisplayProps {
  photos: string[];
  captions?: string[] | string;
  maxPhotos?: number;
}

const AdminPhotoDisplay: React.FC<AdminPhotoDisplayProps> = ({
  photos = [],
  captions = [],
  maxPhotos = 2,
}) => {
  const [photoData, setPhotoData] = useState<PhotoData[]>([]);
  const [loadingStates, setLoadingStates] = useState<boolean[]>([]);
  const [errorStates, setErrorStates] = useState<boolean[]>([]);

  // Initialize photo data and states
  useEffect(() => {
    // Debug logging to help identify caption data issues
    console.log('AdminPhotoDisplay - Received data:', {
      photos,
      captions,
      captionsType: typeof captions,
      maxPhotos
    });

    const processedPhotos = photos.slice(0, maxPhotos).map((photo, index) => {
      // Ensure caption is properly processed from submitted data
      let caption = "";
      
      if (captions) {
        let captionArray = captions;
        
        // Handle case where captions might be a string (comma-separated)
        if (typeof captions === 'string') {
          captionArray = captions.split(',').map((c: string) => c.trim());
        }
        
        // Ensure it's an array and has the caption for this index
        if (Array.isArray(captionArray) && captionArray[index] !== undefined && captionArray[index] !== null) {
          const rawCaption = captionArray[index];
          if (typeof rawCaption === 'string' && rawCaption.trim() !== '') {
            caption = rawCaption.trim();
          }
        }
      }
      
      console.log(`AdminPhotoDisplay - Photo ${index}:`, {
        filename: photo,
        caption: caption,
        rawCaption: captions && Array.isArray(captions) ? captions[index] : 'N/A'
      });
      
      return {
        filename: photo,
        caption: caption,
      };
    });

    setPhotoData(processedPhotos);
    setLoadingStates(new Array(processedPhotos.length).fill(true));
    setErrorStates(new Array(processedPhotos.length).fill(false));
  }, [photos, captions, maxPhotos]);

  const handleImageLoad = (index: number) => {
    setLoadingStates(prev => {
      const newStates = [...prev];
      newStates[index] = false;
      return newStates;
    });
  };

  const handleImageError = (index: number) => {
    setLoadingStates(prev => {
      const newStates = [...prev];
      newStates[index] = false;
      return newStates;
    });
    setErrorStates(prev => {
      const newStates = [...prev];
      newStates[index] = true;
      return newStates;
    });
  };

  const validateImageSource = (filename: string): string => {
    if (!filename) return "";
    
    // Clean the filename - remove any existing uploads/ prefix and backslashes
    let cleanFilename = filename.trim();
    if (!cleanFilename) return "";
    
    // Check if it's already a Cloudinary URL or other full URL
    if (cleanFilename.startsWith("http://") || cleanFilename.startsWith("https://")) {
      // Use Cloudinary URL or other full URL directly
      console.log('Image URL (Cloudinary):', { original: filename, final: cleanFilename });
      return cleanFilename;
    }
    
    // Remove any existing uploads/ prefix to avoid double paths
    cleanFilename = cleanFilename.replace(/^uploads[\/\\]/, "");
    // Convert Windows backslashes to forward slashes
    cleanFilename = cleanFilename.replace(/\\/g, "/");
    
    // Construct the full URL - use the base URL without /api for static files
    const baseUrl = BASE_API_URL.replace("/api", "");
    const fullUrl = `${baseUrl}/uploads/${cleanFilename}`;
    
    console.log('Image URL constructed:', { original: filename, cleaned: cleanFilename, final: fullUrl });
    
    // Return URL without cache busting for better reliability
    return fullUrl;
  };

  // Always render the layout, but show appropriate content based on state

  return (
    <PhotoSectionWrapper>
      <PhotoGridContainer>
        {/* Always render exactly 2 slots to maintain consistent layout */}
        {Array.from({ length: maxPhotos }).map((_, index) => {
          const photo = photoData[index];
          const hasPhoto = !!photo;
          
          return (
            <PhotoItemContainer key={index}>
              <ImagePreviewContainer>
                {!hasPhoto ? (
                  <FallbackContainer>
                    <Typography variant="caption" color="#999">
                      No photo
                    </Typography>
                  </FallbackContainer>
                ) : errorStates[index] ? (
                  <FallbackContainer>
                    <BrokenImageIcon sx={{ fontSize: 40, color: "#f44336" }} />
                    <Typography variant="caption" color="#f44336">
                      Image not found
                    </Typography>
                    <Typography variant="caption" color="#666" style={{ fontSize: "10px" }}>
                      {photo.filename}
                    </Typography>
                  </FallbackContainer>
                ) : (
                  <>
                    <StyledImage
                      src={validateImageSource(photo.filename)}
                      alt={`Report Photo ${index + 1}${photo.caption ? `: ${photo.caption}` : ''}`}
                      onLoad={() => handleImageLoad(index)}
                      onError={(e) => {
                        console.error(`Failed to load image ${index}:`, photo.filename, e);
                        handleImageError(index);
                      }}
                      style={{
                        display: loadingStates[index] ? "none" : "block",
                      }}
                      loading="eager"
                      crossOrigin="anonymous"
                      onLoadStart={() => console.log(`Loading image ${index}:`, photo.filename)}
                    />
                    {loadingStates[index] && (
                      <FallbackContainer>
                        <Typography variant="caption" color="#666">
                          Loading image...
                        </Typography>
                      </FallbackContainer>
                    )}
                  </>
                )}
              </ImagePreviewContainer>
              <CaptionContainer>
                {hasPhoto && photo.caption && photo.caption.trim() !== '' 
                  ? <SafeHtmlRenderer htmlContent={photo.caption.trim()} />
                  : "No caption provided"
                }
              </CaptionContainer>
            </PhotoItemContainer>
          );
        })}
      </PhotoGridContainer>
    </PhotoSectionWrapper>
  );
};

export default AdminPhotoDisplay;
