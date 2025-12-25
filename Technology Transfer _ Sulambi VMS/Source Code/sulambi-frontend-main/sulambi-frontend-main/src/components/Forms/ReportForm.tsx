import SendIcon from "@mui/icons-material/Send";
import PrimaryButton from "../Buttons/PrimaryButton";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import FormGeneratorTemplate, {
  FormGenTemplateProps,
} from "./FormGeneratorTemplate";
import ConfirmModal from "../Modal/ConfirmModal";
import PhotoUploadWithCaptions from "../Inputs/PhotoUploadWithCaptions";
import { useContext, useEffect, useState } from "react";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { createReport } from "../../api/reports";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

interface Props {
  type: "external" | "internal";
  eventId: number;
  open: boolean;
  setOpen?: (state: boolean) => void;
  onSubmit?: () => void;
  hideSubmit?: boolean;
  componentsBeforeSubmit?: React.ReactNode;
}

const ReportForm: React.FC<Props> = (props) => {
  const {
    eventId,
    open,
    type,
    onSubmit,
    componentsBeforeSubmit,
    hideSubmit,
    setOpen,
  } = props;
  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);

  const [openConfirmModal, setOpenConfirmModal] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<string[]>([]);
  const [formRefreshKey, setFormRefreshKey] = useState(0);

  // initial form state - reset when form is opened
  useEffect(() => {
    if (open) {
      // Always reset form data when opening to ensure clean state
      setFormData({});
      setFieldErrors([]);
      setOpenConfirmModal(false);
      // Force refresh the form template to clear any residual state
      setFormRefreshKey(prev => prev + 1);
    }
  }, [open]);

  const submitAction = () => {
    setOpenConfirmModal(true);
  };

  const confirmedSubmitAction = () => {
    const formUploadable = new FormData();
    formUploadable.append("eventId", eventId.toString());
    formUploadable.append("narrative", formData.narrative ?? "");

    // Handle photos with captions
    if (formData.photos && Array.isArray(formData.photos)) {
      formData.photos.forEach((photoWithCaption: any, index: number) => {
        if (photoWithCaption.file) {
          formUploadable.append(`photo_${index}`, photoWithCaption.file);
          formUploadable.append(`photo_caption_${index}`, photoWithCaption.caption || "");
        }
      });
    }

    if (type === "internal") {
      formUploadable.append("budgetUtilized", formData.budgetUtilized ?? "");
      formUploadable.append(
        "budgetUtilizedSrc",
        formData.budgetUtilizedSrc ?? ""
      );
      formUploadable.append("psAttribution", formData.psAttribution ?? "");
      formUploadable.append(
        "psAttributionSrc",
        formData.psAttributionSrc ?? ""
      );
    }

    createReport(eventId, type, formUploadable)
      .then(() => {
        showSnackbarMessage("Successfully submitted report", "success");
        setOpen && setOpen(false);
        setFormData({});
      })
      .catch((err) => {
        if (err.response.data) {
          const message = err.response.data.message;
          const errors = err.response.data.fieldError ?? [];

          setFieldErrors(errors);
          showSnackbarMessage(`Error Occured: ${message}`, "error");
        } else {
          showSnackbarMessage(
            "An error Occured when registering membership",
            "error"
          );
        }
      })
      .finally(() => onSubmit && onSubmit());
  };

  const externalReportForm: (FormGenTemplateProps | FormGenTemplateProps[])[] =
    [
      [
        {
          id: "photos",
          type: "component",
          message: "Photo Documentation",
          component: (
            <PhotoUploadWithCaptions
              question="Photo Documentation"
              required={true}
              error={fieldErrors.includes("photos")}
              value={formData.photos || []}
              onChange={(photos) => {
                setFormData({ ...formData, photos });
              }}
            />
          ),
        },
      ],

      {
        id: "narrative",
        type: "textQuestion",
        message: "Narrative Report",
      },
    ];

  const internalReportForm: (FormGenTemplateProps | FormGenTemplateProps[])[] =
    [
      [
        {
          id: "photos",
          type: "component",
          message: "Photo Documentation",
          component: (
            <PhotoUploadWithCaptions
              question="Photo Documentation"
              required={true}
              error={fieldErrors.includes("photos")}
              value={formData.photos || []}
              onChange={(photos) => {
                setFormData({ ...formData, photos });
              }}
            />
          ),
        },
      ],

      {
        id: "narrative",
        type: "textQuestion",
        message: "Narrative of the Project",
      },
      [
        {
          type: "label",
          message: "Financial requirements and Source of Funds",
        },
      ],
      [
        {
          id: "budgetUtilized",
          type: "number",
          message: "Actual Budget Utilized",
        },
        {
          id: "budgetUtilizedSrc",
          type: "text",
          message: "Budget Source",
        },
      ],
      [
        {
          id: "psAttribution",
          type: "number",
          message: "Personal Services (PS) Attribution",
        },
        {
          id: "psAttributionSrc",
          type: "text",
          message: "Budget Source",
        },
      ],
    ];

  return (
    <>
      <ConfirmModal
        title="Report Submission"
        message="Are you sure you want to submit this report? (No updates/edits can be done after submission)"
        acceptText="Yes"
        declineText="No"
        open={openConfirmModal}
        setOpen={setOpenConfirmModal}
        zindex={10}
        onAccept={() => confirmedSubmitAction()}
      />
      <PopupModal
        header="Report Forms"
        subHeader="Submit your event report here"
        open={open}
        setOpen={setOpen}
        width="25vw"
        maxHeight="80vh"
      >
        <form
          style={{
            maxHeight: "50vh",
            overflowY: "auto",
            scrollbarWidth: "thin",
          }}
        >
          <FlexBox
            flexDirection="column"
            alignItems="center"
            marginBottom="20px"
            rowGap="15px"
          >
            {type === "external" ? (
              <FormGeneratorTemplate
                key={`external-${formRefreshKey}`}
                enableAutoFieldCheck
                fieldErrors={fieldErrors}
                template={externalReportForm}
              />
            ) : (
              <FormGeneratorTemplate
                key={`internal-${formRefreshKey}`}
                enableAutoFieldCheck
                fieldErrors={fieldErrors}
                template={internalReportForm}
              />
            )}
          </FlexBox>
          <FlexBox justifyContent="flex-end" marginTop="10px" gap="10px">
            {componentsBeforeSubmit}
            {!hideSubmit && (
              <PrimaryButton
                label="Submit"
                icon={<SendIcon />}
                size="small"
                onClick={submitAction}
              />
            )}
          </FlexBox>
        </form>
      </PopupModal>
    </>
  );
};

export default ReportForm;
