import React, { useState, useRef, useEffect } from "react";
import { Typography, Box, IconButton, TextField } from "@mui/material";
import FlexBox from "../FlexBox";
import DeleteIcon from "@mui/icons-material/Delete";
import AddPhotoAlternateIcon from "@mui/icons-material/AddPhotoAlternate";
import BrokenImageIcon from "@mui/icons-material/BrokenImage";
import { styled } from "@mui/material/styles";

const StyledImageContainer = styled(Box)(() => ({
  position: "relative",
  width: "100%",
  maxWidth: "300px",
  height: "200px",
  border: "2px dashed #bdbdbd",
  borderRadius: "8px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  overflow: "hidden",
  backgroundColor: "#fafafa",
  "&:hover": {
    borderColor: "var(--text-landing)",
    backgroundColor: "#f5f5f5",
  },
}));

const StyledImage = styled("img")({
  width: "100%",
  height: "100%",
  objectFit: "cover",
});

const PhotoItemContainer = styled("figure")({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: "12px",
  flex: "0 1 calc(50% - 12px)",
  minWidth: 0,
  maxWidth: "calc(50% - 12px)",
  boxSizing: "border-box",
  padding: "16px",
  margin: 0, // Reset default figure margin
  transition: "all 0.2s ease-in-out",
  "&:hover": {
    transform: "translateY(-2px)",
  },
  "@media (max-width: 768px)": {
    flex: "1 1 100%",
    maxWidth: "100%",
    padding: "12px",
  },
});

const PhotoGridContainer = styled(Box)({
  display: "flex",
  gap: "20px",
  width: "100%",
  padding: "12px",
  boxSizing: "border-box",
  justifyContent: "center",
  alignItems: "flex-start",
  "@media (max-width: 768px)": {
    flexDirection: "column",
    gap: "16px",
    padding: "8px",
  },
});

const ImagePreviewContainer = styled(Box)({
  position: "relative",
  width: "100%",
  height: "160px",
  borderRadius: "8px",
  overflow: "hidden",
  backgroundColor: "#f8f9fa",
  boxSizing: "border-box",
  transition: "all 0.2s ease-in-out",
  "&:hover": {
    transform: "scale(1.02)",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
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

const StyledDeleteButton = styled(IconButton)({
  position: "absolute",
  top: "8px",
  right: "8px",
  backgroundColor: "rgba(255, 255, 255, 0.8)",
  "&:hover": {
    backgroundColor: "rgba(255, 255, 255, 0.9)",
  },
});

interface PhotoWithCaption {
  file: File;
  caption: string;
  preview: string;
  isValid?: boolean;
  hasError?: boolean;
}

interface PhotoUploadWithCaptionsProps {
  question: string;
  required?: boolean;
  error?: boolean;
  value?: PhotoWithCaption[];
  onChange?: (photos: PhotoWithCaption[]) => void;
  flex?: number;
}

const PhotoUploadWithCaptions: React.FC<PhotoUploadWithCaptionsProps> = ({
  question,
  required = false,
  error = false,
  value = [],
  onChange,
  flex = 1,
}) => {
  const [photos, setPhotos] = useState<PhotoWithCaption[]>(value);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sync with external value changes (for state persistence)
  useEffect(() => {
    if (value && value !== photos) {
      setPhotos(value);
    }
  }, [value]);

  // Cleanup object URLs when component unmounts or photos change
  useEffect(() => {
    return () => {
      photos.forEach(photo => {
        if (photo.preview && photo.preview.startsWith('blob:')) {
          URL.revokeObjectURL(photo.preview);
        }
      });
    };
  }, [photos]);

  const validateImage = (file: File): Promise<boolean> => {
    return new Promise((resolve) => {
      const img = new Image();
      const url = URL.createObjectURL(file);
      
      img.onload = () => {
        URL.revokeObjectURL(url);
        resolve(true);
      };
      
      img.onerror = () => {
        URL.revokeObjectURL(url);
        resolve(false);
      };
      
      img.src = url;
    });
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const newPhotos: PhotoWithCaption[] = [];
    
    // Limit to 2 images total
    const remainingSlots = 2 - photos.length;
    const filesToProcess = Array.from(files).slice(0, remainingSlots);

    for (const file of filesToProcess) {
      if (file.type.startsWith("image/")) {
        const isValid = await validateImage(file);
        const preview = URL.createObjectURL(file);
        
        newPhotos.push({
          file,
          caption: "",
          preview,
          isValid,
          hasError: !isValid,
        });
      }
    }

    const updatedPhotos = [...photos, ...newPhotos];
    setPhotos(updatedPhotos);
    onChange?.(updatedPhotos);

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleRemovePhoto = (index: number) => {
    const updatedPhotos = photos.filter((_, i) => i !== index);
    setPhotos(updatedPhotos);
    onChange?.(updatedPhotos);
  };

  const handleCaptionChange = (index: number, caption: string) => {
    const updatedPhotos = photos.map((photo, i) =>
      i === index ? { ...photo, caption } : photo
    );
    setPhotos(updatedPhotos);
    onChange?.(updatedPhotos);
  };

  const handleAddPhoto = () => {
    fileInputRef.current?.click();
  };

  return (
    <FlexBox flexDirection="column" flex={flex} width="100%">
      <Typography color={error ? "red" : "var(--text-landing)"} marginBottom="10px">
        {question}
        {required && <b style={{ color: "red" }}>*</b>}
      </Typography>

      {/* Photo Display Grid - Horizontal Layout */}
      <PhotoGridContainer>
        {photos.map((photo, index) => (
          <PhotoItemContainer key={index}>
            <ImagePreviewContainer>
              {photo.hasError ? (
                <FallbackContainer>
                  <BrokenImageIcon sx={{ fontSize: 40, color: "#f44336" }} />
                  <Typography variant="caption" color="#f44336">
                    Invalid Image
                  </Typography>
                </FallbackContainer>
              ) : (
                <>
                  <StyledImage 
                    src={photo.preview} 
                    alt={`Upload ${index + 1}${photo.caption ? `: ${photo.caption}` : ''}`}
                    onError={() => {
                      // Handle runtime image loading errors
                      console.warn(`Failed to load image: ${photo.preview}`);
                      const updatedPhotos = photos.map((p, i) => 
                        i === index ? { ...p, hasError: true, isValid: false } : p
                      );
                      setPhotos(updatedPhotos);
                      onChange?.(updatedPhotos);
                    }}
                    onLoad={() => {
                      // Ensure image is marked as valid when it loads successfully
                      if (photo.hasError) {
                        const updatedPhotos = photos.map((p, i) => 
                          i === index ? { ...p, hasError: false, isValid: true } : p
                        );
                        setPhotos(updatedPhotos);
                        onChange?.(updatedPhotos);
                      }
                    }}
                  />
                  <StyledDeleteButton
                    size="small"
                    onClick={() => handleRemovePhoto(index)}
                  >
                    <DeleteIcon fontSize="small" />
                  </StyledDeleteButton>
                </>
              )}
            </ImagePreviewContainer>
            <TextField
              size="small"
              placeholder="Enter caption for this photo..."
              value={photo.caption}
              onChange={(e) => handleCaptionChange(index, e.target.value)}
              fullWidth
              variant="outlined"
              error={photo.hasError}
              helperText={photo.hasError ? "Invalid image file" : ""}
              inputProps={{
                "aria-label": `Caption for photo ${index + 1}`,
                "aria-describedby": `photo-${index}-description`
              }}
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: "6px",
                  fontSize: "12px",
                  backgroundColor: "#f9fafb",
                  border: "1px solid #e5e7eb",
                  transition: "all 0.2s ease-in-out",
                  "&:hover": {
                    borderColor: "#9ca3af",
                    backgroundColor: "#ffffff",
                  },
                  "&.Mui-focused": {
                    borderColor: "#4a90e2",
                    backgroundColor: "#ffffff",
                    boxShadow: "0 0 0 2px rgba(74, 144, 226, 0.1)",
                  },
                },
                "& .MuiInputBase-input": {
                  fontSize: "12px",
                  padding: "8px 12px",
                  color: "#374151",
                  fontWeight: "500",
                  textAlign: "center",
                },
                "& .MuiFormHelperText-root": {
                  fontSize: "10px",
                  marginTop: "4px",
                },
                "& .MuiOutlinedInput-notchedOutline": {
                  border: "none",
                },
              }}
            />
          </PhotoItemContainer>
        ))}

        {/* Add Photo Button - Only show if less than 2 photos */}
        {photos.length < 2 && (
          <PhotoItemContainer>
            <StyledImageContainer
              onClick={handleAddPhoto}
              sx={{
                cursor: "pointer",
                flexDirection: "column",
                gap: "8px",
                height: "180px",
                maxWidth: "none",
              }}
            >
              <AddPhotoAlternateIcon sx={{ fontSize: 40, color: "#bdbdbd" }} />
              <Typography color="#bdbdbd" variant="body2" textAlign="center">
                Click to add photo<br />({photos.length}/2)
              </Typography>
            </StyledImageContainer>
            {/* Empty space for caption alignment */}
            <Box height="56px" />
          </PhotoItemContainer>
        )}
      </PhotoGridContainer>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileSelect}
        style={{ display: "none" }}
      />

      {/* Helper Text */}
      <Typography variant="caption" color="#666" marginTop="5px">
        Maximum 2 images allowed. Each image can have a caption.
      </Typography>
    </FlexBox>
  );
};

export default PhotoUploadWithCaptions;
