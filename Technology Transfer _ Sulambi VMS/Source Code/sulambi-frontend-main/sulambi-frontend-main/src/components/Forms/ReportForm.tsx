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
import { createReport, updateReport } from "../../api/reports";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

interface Props {
  type: "external" | "internal";
  eventId: number;
  open: boolean;
  setOpen?: (state: boolean) => void;
  onSubmit?: () => void;
  hideSubmit?: boolean;
  componentsBeforeSubmit?: React.ReactNode;
  reportId?: number; // For edit mode
  initialData?: any; // Pre-filled data for edit mode
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
    reportId,
    initialData,
  } = props;
  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);

  const [openConfirmModal, setOpenConfirmModal] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<string[]>([]);
  const [formRefreshKey, setFormRefreshKey] = useState(0);
  const isEditMode = !!reportId && !!initialData;

  // initial form state - reset when form is opened or pre-fill for edit mode
  useEffect(() => {
    if (open) {
      if (isEditMode && initialData) {
        // Pre-fill form data for edit mode
        const photosWithCaptions: Array<{
          file: File | null;
          url: string;
          preview: string;
          caption: string;
        }> = [];
        if (initialData.photos && Array.isArray(initialData.photos)) {
          const captions = initialData.photoCaptions || [];
          initialData.photos.forEach((photo: string, index: number) => {
            photosWithCaptions.push({
              file: null, // Existing photos don't have File objects
              url: photo, // URL to existing photo
              preview: photo, // Keep existing photo visible/editable in upload grid
              caption: captions[index] || "",
            });
          });
        }
        setFormData({
          narrative: initialData.narrative || "",
          photos: photosWithCaptions,
          approvedBudget: initialData.approvedBudget || "",
          approvedBudgetSrc: initialData.approvedBudgetSrc || "",
          budgetUtilized: initialData.budgetUtilized || "",
          budgetUtilizedSrc: initialData.budgetUtilizedSrc || "",
          psAttribution: initialData.psAttribution || "",
          psAttributionSrc: initialData.psAttributionSrc || "",
        });
      } else {
        // Reset form data when creating new report
        setFormData({});
      }
      setFieldErrors([]);
      setOpenConfirmModal(false);
      // Force refresh the form template to clear any residual state
      setFormRefreshKey(prev => prev + 1);
    }
  }, [open, isEditMode, initialData]);

  const submitAction = (event?: React.MouseEvent<HTMLButtonElement>) => {
    // Prevent parent <form> native submit from interfering with modal open behavior.
    event?.preventDefault();
    event?.stopPropagation();
    console.log("[REPORT_FORM] Submit clicked", {
      isEditMode,
      eventId,
      reportId,
      type,
      hasFormData: !!formData,
    });
    setOpenConfirmModal(true);
  };

  const confirmedSubmitAction = () => {
    console.log("[REPORT_FORM] Confirmed submit", {
      isEditMode,
      eventId,
      reportId,
      type,
      formData,
    });
    const formUploadable = new FormData();
    formUploadable.append("eventId", eventId.toString());
    formUploadable.append("narrative", formData.narrative ?? "");

    // Handle photos with captions - only include new photos (with file property)
    if (formData.photos && Array.isArray(formData.photos)) {
      console.log("[REPORT_FORM] Preparing photos for upload", {
        totalPhotoEntries: formData.photos.length,
        uploadableCount: formData.photos.filter((p: any) => !!p?.file).length,
      });

      // Persist existing edited photo list (kept/removed + captions) during report update.
      if (isEditMode) {
        const existingPhotos = formData.photos
          .filter((p: any) => !p?.file && !!(p?.url || p?.preview))
          .map((p: any) => String(p.url || p.preview).trim())
          .filter(Boolean);
        const existingPhotoCaptions = formData.photos
          .filter((p: any) => !p?.file && !!(p?.url || p?.preview))
          .map((p: any) => String(p.caption || ""));
        formUploadable.append("existingPhotos", JSON.stringify(existingPhotos));
        formUploadable.append("existingPhotoCaptions", JSON.stringify(existingPhotoCaptions));
        console.log("[REPORT_FORM] Existing photos payload for update", {
          existingCount: existingPhotos.length,
          existingPhotos,
        });
      }

      formData.photos.forEach((photoWithCaption: any, index: number) => {
        // Only upload if it's a new file (not an existing URL)
        if (photoWithCaption.file) {
          console.log("[REPORT_FORM] Appending photo to FormData", {
            field: `photo_${index}`,
            captionField: `photo_caption_${index}`,
            name: photoWithCaption.file.name,
            size: photoWithCaption.file.size,
            type: photoWithCaption.file.type,
            captionLength: String(photoWithCaption.caption || "").length,
          });
          formUploadable.append(`photo_${index}`, photoWithCaption.file);
          formUploadable.append(`photo_caption_${index}`, photoWithCaption.caption || "");
        } else {
          console.log("[REPORT_FORM] Skipping photo entry without File object", {
            index,
            hasUrl: !!photoWithCaption?.url,
          });
        }
      });
    }

    if (type === "internal") {
      formUploadable.append("approvedBudget", formData.approvedBudget ?? "");
      formUploadable.append("approvedBudgetSrc", formData.approvedBudgetSrc ?? "");
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

    const submitPromise = isEditMode && reportId
      ? updateReport(reportId, type, formUploadable)
      : createReport(eventId, type, formUploadable);

    submitPromise
      .then(() => {
        showSnackbarMessage(
          isEditMode 
            ? "Successfully updated report" 
            : "Successfully submitted report",
          "success"
        );
        setOpen && setOpen(false);
        setFormData({});
      })
      .catch((err) => {
        if (err.response?.data) {
          const message = err.response.data.message;
          const errors = err.response.data.fieldError ?? [];

          setFieldErrors(errors);
          showSnackbarMessage(`Error Occurred: ${message}`, "error");
        } else {
          showSnackbarMessage(
            "An error occurred when submitting the report",
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
              value={formData.photos}
              onChange={(photos) => {
                setFormData((prev: any) => ({ ...prev, photos }));
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
              value={formData.photos}
              onChange={(photos) => {
                setFormData((prev: any) => ({ ...prev, photos }));
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
          id: "approvedBudget",
          type: "text",
          message: "Approved Budget as Proposed",
        },
        {
          id: "approvedBudgetSrc",
          type: "text",
          message: "Budget Source",
        },
      ],
      [
        {
          id: "budgetUtilized",
          type: "text",
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
          type: "text",
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
        title={isEditMode ? "Update Report" : "Report Submission"}
        message={
          isEditMode
            ? "Are you sure you want to update this report?"
            : "Are you sure you want to submit this report?"
        }
        acceptText="Yes"
        declineText="No"
        open={openConfirmModal}
        setOpen={setOpenConfirmModal}
        zindex={12000}
        onAccept={() => confirmedSubmitAction()}
      />
      <PopupModal
        header="Report Forms"
        subHeader={isEditMode ? "Edit your event report here" : "Submit your event report here"}
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
                label={isEditMode ? "Update" : "Submit"}
                icon={<SendIcon />}
                size="small"
                type="button"
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
