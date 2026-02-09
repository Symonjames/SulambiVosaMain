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
import dayjs from "dayjs";

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

  const { formData, setFormData, immutableSetFormData } = useContext(FormDataContext);
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

    // Personal details: use form fields first, then membership cache
    let member: Partial<MembershipType> = {};
    try {
      const cache = localStorage.getItem("membershipCache");
      if (cache) member = JSON.parse(cache);
    } catch (_) {}
    const fullname = formData.fullname ?? member.fullname;
    const email = formData.email ?? member.email;
    const srcode = formData.srcode ?? member.srcode;
    const age = formData.age ?? member.age;
    let birthday = formData.birthday ?? member.birthday;
    if (typeof birthday === "number" && birthday) birthday = dayjs(birthday).format("MMMM D, YYYY");
    const sex = formData.sex ?? member.sex;
    const campus = formData.campus ?? member.campus;
    const collegeDept = formData.collegeDept ?? member.collegeDept;
    const yrlevelprogram = formData.yrlevelprogram ?? member.yrlevelprogram;
    const address = formData.address ?? member.address;
    const contactNum = formData.contactNum ?? member.contactNum;
    const fblink = formData.fblink ?? member.fblink;
    if (fullname) formUploadable.append("fullname", String(fullname));
    if (email) formUploadable.append("email", String(email));
    if (srcode) formUploadable.append("srcode", String(srcode));
    if (age !== undefined && age !== "") formUploadable.append("age", String(age));
    if (birthday) formUploadable.append("birthday", String(birthday));
    if (sex) formUploadable.append("sex", String(sex));
    if (campus) formUploadable.append("campus", String(campus));
    if (collegeDept) formUploadable.append("collegeDept", String(collegeDept));
    if (yrlevelprogram) formUploadable.append("yrlevelprogram", String(yrlevelprogram));
    if (address) formUploadable.append("address", String(address));
    if (contactNum) formUploadable.append("contactNum", String(contactNum));
    if (fblink) formUploadable.append("fblink", String(fblink));
    try {
      if ((member as any).affiliation) formUploadable.append("affiliation", String((member as any).affiliation));
    } catch (_) {}

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

  // Reset form when modal opens; pre-fill personal details from membership cache when available
  useEffect(() => {
    setForceRefresh(forceRefresh + 1);
    if (open) {
      afterOpen && afterOpen();
      setFieldErrors([]);
      if (viewOnly) return;
      if (preventLoadingCache) {
        try {
          const cache = localStorage.getItem("membershipCache");
          if (cache) {
            const member = JSON.parse(cache) as Partial<MembershipType>;
            const prefill: Record<string, unknown> = {};
            if (member.fullname != null) prefill.fullname = member.fullname;
            if (member.email != null) prefill.email = member.email;
            if (member.srcode != null) prefill.srcode = member.srcode;
            if (member.birthday != null) prefill.birthday = member.birthday;
            if (member.age != null) prefill.age = member.age;
            if (member.sex != null) prefill.sex = member.sex;
            if (member.campus != null) prefill.campus = member.campus;
            if (member.collegeDept != null) prefill.collegeDept = member.collegeDept;
            if (member.yrlevelprogram != null) prefill.yrlevelprogram = member.yrlevelprogram;
            if (member.address != null) prefill.address = member.address;
            if (member.contactNum != null) prefill.contactNum = member.contactNum;
            if (member.fblink != null) prefill.fblink = member.fblink;
            if (Object.keys(prefill).length > 0) immutableSetFormData(prefill);
          }
        } catch (_) {}
      } else {
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
              { type: "section", message: "Personal Details" },
              [{ id: "fullname", type: "text", required: true, message: "Full Name" }],
              [
                { id: "email", type: "text", required: true, message: "GSuite Email" },
                { id: "srcode", type: "text", required: true, message: "SR-Code" },
              ],
              [
                { id: "birthday", type: "date", required: true, message: "Birth Date" },
                {
                  id: "age",
                  type: "number",
                  required: true,
                  message: "Age",
                  onUse: (e: any) => {
                    const raw = String(e?.target?.value ?? "").replace(/\D+/g, "").slice(0, 2);
                    if (raw !== (e?.target?.value ?? "")) immutableSetFormData({ age: raw });
                  },
                },
                {
                  id: "sex",
                  type: "dropdown",
                  required: true,
                  message: "Sex",
                  menu: [
                    { key: "Male", value: "male" },
                    { key: "Female", value: "female" },
                  ],
                },
              ],
              [
                { id: "campus", type: "text", required: true, message: "Campus" },
                { id: "collegeDept", type: "text", required: true, message: "College Department" },
              ],
              [
                { id: "yrlevelprogram", type: "text", required: true, message: "Year Level & Program" },
                { id: "address", type: "text", required: true, message: "Address" },
              ],
              [
                { id: "contactNum", type: "text", required: true, message: "Contact Number" },
                { id: "fblink", type: "text", message: "Facebook Link" },
              ],
              { type: "section", message: "Documents" },
              [
                {
                  id: "medCert",
                  type: "file",
                  required: true,
                  message: "Medical Certificate *",
                  accept: ".pdf,.doc,.docx",
                },
                {
                  id: "waiver",
                  type: "file",
                  message: "Waiver *",
                  required: true,
                  accept: ".pdf,.doc,.docx",
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
