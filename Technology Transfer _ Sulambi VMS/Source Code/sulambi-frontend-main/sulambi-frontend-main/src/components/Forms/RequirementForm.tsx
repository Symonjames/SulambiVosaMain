import { useContext, useEffect, useState } from "react";
import PrimaryButton from "../Buttons/PrimaryButton";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import FormGeneratorTemplate from "./FormGeneratorTemplate";
import SendIcon from "@mui/icons-material/Send";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { uploadRequirements } from "../../api/requirements";
import { SnackbarContext } from "../../contexts/SnackbarProvider";
import { MembershipType } from "../../interface/types";

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
  const [fieldErrors, setFieldErrors] = useState<string[]>([]);

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

    // Attach member details when available (used by Requirement Evaluation table)
    // This is optional server-side, but without it officers will see "N/A" for participant name.
    try {
      const cache = localStorage.getItem("membershipCache");
      if (cache) {
        const member: Partial<MembershipType> = JSON.parse(cache);
        if (member.fullname) formUploadable.append("fullname", String(member.fullname));
        if (member.email) formUploadable.append("email", String(member.email));
        if (member.srcode) formUploadable.append("srcode", String(member.srcode));
        if (member.age !== undefined) formUploadable.append("age", String(member.age));
        if (member.birthday) formUploadable.append("birthday", String(member.birthday));
        if (member.sex) formUploadable.append("sex", String(member.sex));
        if (member.campus) formUploadable.append("campus", String(member.campus));
        if (member.collegeDept) formUploadable.append("collegeDept", String(member.collegeDept));
        if (member.yrlevelprogram) formUploadable.append("yrlevelprogram", String(member.yrlevelprogram));
        if (member.address) formUploadable.append("address", String(member.address));
        if (member.contactNum) formUploadable.append("contactNum", String(member.contactNum));
        if (member.fblink) formUploadable.append("fblink", String(member.fblink));
        // Backend expects affiliation; membership has it
        if ((member as any).affiliation) {
          formUploadable.append("affiliation", String((member as any).affiliation));
        }
      }
    } catch (e) {
      // Non-fatal: still allow uploading requirements files
      console.warn("RequirementForm: failed to read membershipCache for participant details", e);
    }

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
      .then((response) => {
        console.log("[RequirementForm] ✅ Successfully uploaded requirements:", response.data);
        showSnackbarMessage("Requirements Uploaded Succesfully", "success");
        setOpen && setOpen(false);
        // Clear form data after successful submission
        setFormData({});
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
      // Clear formData only when uploading (viewOnly needs the passed-in record to view uploaded files)
      if (!viewOnly && !preventLoadingCache) {
        setFormData({});
      }
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
