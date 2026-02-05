import { useContext, useEffect, useState } from "react";
import PrimaryButton from "../Buttons/PrimaryButton";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import FormGeneratorTemplate, { FormGenTemplateProps } from "./FormGeneratorTemplate";
import SendIcon from "@mui/icons-material/Send";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { uploadRequirements, uploadRequirementsPublicEvent } from "../../api/requirements";
import { SnackbarContext } from "../../contexts/SnackbarProvider";
import { MembershipType } from "../../interface/types";

interface Props {
  open: boolean;
  eventId: number;
  eventType: "external" | "internal";
  viewOnly?: boolean;
  preventLoadingCache?: boolean;
  isPublicJoin?: boolean;
  setOpen?: (state: boolean) => void;
  afterOpen?: () => void;
}

const RequirementForm: React.FC<Props> = ({
  open,
  eventId,
  eventType,
  viewOnly,
  preventLoadingCache,
  isPublicJoin = false,
  setOpen,
  afterOpen,
}) => {
  const [forceRefresh, setForceRefresh] = useState(0);
  const [fieldErrors, setFieldErrors] = useState<string[]>([]);

  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);

  const submitCallback = () => {
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

    if (isPublicJoin) {
      const fullname = (formData.fullname ?? "").toString().trim();
      const email = (formData.email ?? "").toString().trim();
      if (!fullname || !email) {
        setFieldErrors(["fullname", "email"].filter((k) => !(formData as any)[k]));
        showSnackbarMessage("Full name and email are required for temporary volunteer registration.", "error");
        return;
      }
    }

    const formUploadable = new FormData();
    formUploadable.append("type", eventType);

    if (isPublicJoin) {
      formUploadable.append("fullname", (formData.fullname ?? "").toString());
      formUploadable.append("email", (formData.email ?? "").toString());
      if (formData.contactNum != null) formUploadable.append("contactNum", String(formData.contactNum));
      if (formData.srcode != null) formUploadable.append("srcode", String(formData.srcode));
      if (formData.age != null) formUploadable.append("age", String(formData.age));
      if (formData.birthday != null) formUploadable.append("birthday", String(formData.birthday));
      if (formData.sex != null) formUploadable.append("sex", String(formData.sex));
      if (formData.address != null) formUploadable.append("address", String(formData.address));
      if (formData.fblink != null) formUploadable.append("fblink", String(formData.fblink));
    } else {
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
          if ((member as any).affiliation) formUploadable.append("affiliation", String((member as any).affiliation));
        }
      } catch (e) {
        console.warn("RequirementForm: failed to read membershipCache", e);
      }
    }

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

    const uploadPromise = isPublicJoin
      ? uploadRequirementsPublicEvent(eventId, eventType, formUploadable)
      : uploadRequirements(eventId, formUploadable);

    uploadPromise
      .then(() => {
        showSnackbarMessage(
          isPublicJoin
            ? "You are registered as a volunteer for this event. Access is limited to this event only."
            : "Requirements Uploaded Succesfully",
          "success"
        );
        setOpen && setOpen(false);
        setFormData({});
      })
      .catch((err) => {
        const message = err.response?.data?.message ?? "An error occurred when submitting.";
        const errors = err.response?.data?.fieldError ?? [];
        setFieldErrors(errors);
        showSnackbarMessage(message, "error");
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

  const baseTemplate: (FormGenTemplateProps | FormGenTemplateProps[])[] = [
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
  ];

  const publicJoinFields: (FormGenTemplateProps | FormGenTemplateProps[])[] = isPublicJoin
    ? [
        [
          { id: "fullname", type: "text" as const, message: "Full Name", required: true },
          { id: "email", type: "text" as const, message: "Email", required: true },
        ],
        [{ id: "contactNum", type: "text" as const, message: "Contact Number" }],
      ]
    : [];

  const template = [...publicJoinFields, ...baseTemplate];

  return (
    <PopupModal
      header={isPublicJoin ? "Join as volunteer (this event only)" : "Requirement Form"}
      subHeader={isPublicJoin ? "Complete the form to join this public event as a temporary volunteer. Access is limited to this event." : "Kindly fill up the information needed below"}
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
            template={template}
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
