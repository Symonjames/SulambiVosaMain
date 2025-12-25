import { useContext, useEffect, useState } from "react";
import PrimaryButton from "../Buttons/PrimaryButton";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import FormGeneratorTemplate from "./FormGeneratorTemplate";
import SendIcon from "@mui/icons-material/Send";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { uploadRequirements } from "../../api/requirements";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

interface Props {
  open: boolean;
  eventId: number;
  eventType: "external" | "internal";
  viewOnly?: boolean;
  preventLoadingCache?: boolean;
  setOpen?: (state: boolean) => void;
  afterOpen?: () => void;
}

const RequirementForm: React.FC<Props> = ({
  open,
  eventId,
  eventType,
  viewOnly,
  preventLoadingCache,
  setOpen,
  afterOpen,
}) => {
  const [forceRefresh, setForceRefresh] = useState(0);
  const [fieldErrors, setFieldErrors] = useState([]);

  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);

  const submitCallback = () => {
    // Validate that both files are present
    const hasMedCert = formData.medCert instanceof File || 
                      (formData.medCert instanceof FileList && formData.medCert.length > 0);
    const hasWaiver = formData.waiver instanceof File || 
                    (formData.waiver instanceof FileList && formData.waiver.length > 0);

    if (!hasMedCert || !hasWaiver) {
      const missing = [];
      if (!hasMedCert) missing.push("medCert");
      if (!hasWaiver) missing.push("waiver");
      setFieldErrors(missing);
      showSnackbarMessage(`Please upload: ${missing.join(", ")}`, "error");
      return;
    }

    // Only send medCert and waiver - nothing else is required
    const formUploadable = new FormData();
    formUploadable.append("type", eventType);

    // Only append medCert and waiver files
    if (formData.medCert instanceof File) {
      formUploadable.append("medCert", formData.medCert);
    } else if (formData.medCert instanceof FileList && formData.medCert.length > 0) {
      formUploadable.append("medCert", formData.medCert[0]);
    }

    if (formData.waiver instanceof File) {
      formUploadable.append("waiver", formData.waiver);
    } else if (formData.waiver instanceof FileList && formData.waiver.length > 0) {
      formUploadable.append("waiver", formData.waiver[0]);
    }

    uploadRequirements(eventId, formUploadable)
      .then(() => {
        showSnackbarMessage("Requirements Uploaded Succesfully", "success");
        setOpen && setOpen(false);
      })
      .catch((err) => {
        if (err.response?.data) {
          const message = err.response.data.message;
          const errors = err.response.data.fieldError ?? [];

          setFieldErrors(errors);
          showSnackbarMessage(`Error Occured: ${message}`, "error");
        } else {
          showSnackbarMessage(
            "An error Occured when uploading requirements",
            "error"
          );
        }
      });
  };

  // Reset form when modal opens
  useEffect(() => {
    setForceRefresh(forceRefresh + 1);
    if (open) {
      afterOpen && afterOpen();
      setFieldErrors([]);
      // Clear formData - files will be set when user selects them
      setFormData({});
    }
  }, [open]);

  return (
    <PopupModal
      header="Requirement Form"
      subHeader="Kindly fill up the information needed below"
      open={open}
      setOpen={setOpen}
    >
      <form
        style={{
          maxHeight: "55vh",
          overflowY: "auto",
          scrollbarWidth: "thin",
        }}
      >
        <FlexBox flexDirection="column" alignItems="center" rowGap="15px">
          <FormGeneratorTemplate
            enableAutoFieldCheck
            viewOnly={viewOnly}
            forceRefresh={forceRefresh}
            fieldErrors={fieldErrors}
            template={[
              [
                {
                  id: "medCert",
                  type: "file",
                  required: true,
                  message: "Medical Certificate",
                },
                {
                  id: "waiver",
                  type: "file",
                  message: "Waiver",
                  required: true,
                },
              ],
              [
                {
                  type: "component",
                  component: (
                    <PrimaryButton
                      label="Download Waiver Template"
                      sx={{ width: "100%" }}
                      onClick={() => {
                        window.open(
                          "https://docs.google.com/document/d/1fCd3h3YdqivXm6uEPDDg3_8QXz0CBG3e/edit"
                        );
                      }}
                    />
                  ),
                },
              ],
            ]}
          />
        </FlexBox>
      </form>
      <FlexBox justifyContent="flex-end" marginTop="10px">
        {!viewOnly && (
          <PrimaryButton
            label="Submit"
            size="small"
            icon={<SendIcon />}
            onClick={submitCallback}
          />
        )}
      </FlexBox>
    </PopupModal>
  );
};

export default RequirementForm;
