import { Alert, Snackbar, SnackbarCloseReason } from "@mui/material";
import { createContext, ReactNode, useState } from "react";

export interface SnackbarDataType {
  showSnackbarMessage: (
    message: string,
    type?: "info" | "success" | "error" | "warning"
  ) => void;
}

export const SnackbarContext = createContext<SnackbarDataType>({
  showSnackbarMessage: () => {},
});

const SnackbarProvider = ({ children }: { children: ReactNode }) => {
  const [message, setMessage] = useState("");
  const [showSnack, setShowSnack] = useState(false);
  const [snackbarType, setSnackbarType] = useState<
    "info" | "success" | "error" | "warning"
  >("info");

  const handleClose = (
    _event?: React.SyntheticEvent | Event,
    reason?: SnackbarCloseReason
  ) => {
    if (reason === "clickaway") {
      return;
    }

    setShowSnack(false);
  };

  const showSnackbarMessage = (
    msg: string,
    snackbarType?: "info" | "success" | "error" | "warning"
  ) => {
    setSnackbarType(snackbarType ?? "info");
    setMessage(msg);
    setShowSnack(true);
    setTimeout(() => setShowSnack(false), 3000);
  };

  return (
    <SnackbarContext.Provider value={{ showSnackbarMessage }}>
      <Snackbar
        open={showSnack}
        anchorOrigin={{
          horizontal: "right",
          vertical: "bottom",
        }}
        sx={{
          zIndex: 10001, // Higher than PopupModal (9999/10000) to appear above modals
        }}
      >
        <Alert
          onClose={handleClose}
          severity={snackbarType}
          variant="filled"
          sx={{ 
            width: "100%",
            zIndex: 10001, // Ensure Alert also has high z-index
          }}
        >
          {message}
        </Alert>
      </Snackbar>
      {children}
    </SnackbarContext.Provider>
  );
};

export default SnackbarProvider;
