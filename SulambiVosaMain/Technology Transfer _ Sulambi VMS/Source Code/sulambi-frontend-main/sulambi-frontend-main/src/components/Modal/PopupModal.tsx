import { Box, IconButton, Typography } from "@mui/material";
import { PopUpModalProps } from "../../interface/props";
import CloseIcon from "@mui/icons-material/Close";
import FlexBox from "../FlexBox";
import { useEffect } from "react";
import { useMediaQuery } from "react-responsive";

const PopupModal: React.FC<PopUpModalProps> = ({
  header,
  disableBGShadow,
  hideCloseButton,
  children,
  subHeader,
  minHeight,
  minWidth,
  maxHeight,
  maxWidth,
  smallHeader,
  width,
  zval,
  open,
  setOpen,
  onClose,
}) => {
  // current alternative solution
  useEffect(() => {
    document.body.style.overflow = "hidden";
  }, []);

  useEffect(() => {
    if (!open) document.body.style.overflow = "";
  }, [open]);

  // Handle Esc key to close modal
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && open) {
        setOpen && setOpen(false);
        onClose && onClose();
      }
    };

    if (open) {
      document.addEventListener("keydown", handleEscKey);
    }

    return () => {
      document.removeEventListener("keydown", handleEscKey);
    };
  }, [open, setOpen, onClose]);

  const isMobile = useMediaQuery({
    query: "(max-width: 600px)",
  });

  const isSmallMobile = useMediaQuery({
    query: "(max-width: 390px)",
  });

  return (
    <>
      {open && (
        <FlexBox
          justifyContent="center"
          alignItems={isSmallMobile ? undefined : "center"}
          onClick={(e) => {
            // Close modal when clicking outside the content area
            if (e.target === e.currentTarget) {
              setOpen && setOpen(false);
              onClose && onClose();
            }
          }}
          sx={{
            minHeight: "100vh",
            maxHeight: "100vh",
            width: "100%",
            position: "fixed",
            top: 0,
            left: 0,
            backdropFilter: "blur(3px)",
            zIndex: zval ?? 9999,
            bgcolor: disableBGShadow ? "" : "#00000069",
            animation: "fadeInFromBottom 0.8s forwards",
            overflow: "auto",
          }}
        >
          <Box
            minWidth={isMobile ? "90vw" : minWidth || "40vw"}
            minHeight={minHeight}
            maxWidth={isMobile ? "100%" : maxWidth}
            maxHeight={maxHeight}
            width={width}
            position={"relative"}
            bgcolor="white"
            padding="20px"
            paddingBottom="10px"
            boxShadow="0 0 10px 1px gray"
            borderRadius="10px"
            overflow="auto"
            zIndex={10000}
            onClick={(e) => {
              // Prevent modal from closing when clicking inside the content area
              e.stopPropagation();
            }}
          >
            <FlexBox justifyContent="space-between">
              <Typography
                variant={smallHeader ? "h6" : "h5"}
                fontWeight="bold"
                color="var(--text-landing)"
              >
                {header}
              </Typography>
              {!hideCloseButton ? (
                <IconButton
                  onClick={() =>
                    setOpen && setOpen(false) && onClose && onClose()
                  }
                >
                  <CloseIcon />
                </IconButton>
              ) : (
                <></>
              )}
            </FlexBox>
            <Typography variant="body2" color="var(--text-landing-light)">
              {subHeader}
            </Typography>

            <Box margin="10px 0px">{children}</Box>
          </Box>
        </FlexBox>
      )}
    </>
  );
};

export default PopupModal;
