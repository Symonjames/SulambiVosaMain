import { useContext, useEffect } from "react";
import PrimaryButton from "../Buttons/PrimaryButton";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import FormGeneratorTemplate, {
  FormGenTemplateProps,
} from "./FormGeneratorTemplate";
import SaveIcon from "@mui/icons-material/Save";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { getSignatory, updateSignatories } from "../../api/events";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

interface SignatoriesFormProps {
  open: boolean;
  signatoryId: number;
  setOpen?: (state: boolean) => void;
  onSave?: () => void;
}

const SignatoriesForm: React.FC<SignatoriesFormProps> = ({
  open,
  signatoryId,
  setOpen,
  onSave,
}) => {
  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);

  useEffect(() => {
    if (open && signatoryId !== null && signatoryId !== undefined) {
      // Load existing signatory data when modal opens
      getSignatory(signatoryId)
        .then((response) => {
          // API returns { data: { data: {...}, message: "..." } }
          const signatoryData = response.data?.data || response.data || {};
          setFormData(signatoryData);
        })
        .catch((error) => {
          console.error("Error loading signatory data:", error);
          // Initialize with empty data if load fails
          setFormData({});
        });
    } else if (open) {
      // If modal opens but no signatoryId, clear form
      setFormData({});
    }
  }, [open, signatoryId]);

  const updateSignatoriesCallback = () => {
    updateSignatories(signatoryId, formData)
      .then(() => {
        setOpen && setOpen(false);
        onSave && onSave();
        showSnackbarMessage("Successfully updated signatories", "success");
      })
      .catch(() => {
        showSnackbarMessage(
          "An Error occured in updating signatories",
          "error"
        );
      });
  };

  const Fields: (FormGenTemplateProps | FormGenTemplateProps[])[] = [
    [
      {
        id: "reviewedBy",
        type: "text",
        message: "Reviewed By",
        required: true,
      },
      {
        id: "preparedBy",
        type: "text",
        message: "Prepared By",
        required: true,
      },
    ],
    [
      {
        id: "recommendingApproval1",
        type: "text",
        message: "Recommending Approval (1)",
        required: true,
      },
      {
        id: "recommendingApproval2",
        type: "text",
        message: "Recommending Approval (2)",
        required: true,
      },
    ],
    {
      id: "approvedBy",
      type: "text",
      message: "Approved By",
      required: true,
    },
    {
      type: "divider",
    },

    // titles
    {
      type: "label",
      message:
        "The following are the tiles of the signatories, this part is optional if you want to use the default titles (kindly preview the report form):",
    },
    [
      { id: "reviewedTitle", type: "text", message: "Title of Reviewer" },
      {
        id: "preparedTitle",
        type: "text",
        message: "Preparer's title",
      },
    ],
    [
      {
        id: "recommendingSignatory1",
        type: "text",
        message: "Recommending Approval (1) Title",
      },
      {
        id: "recommendingSignatory2",
        type: "text",
        message: "Recommending Approval (2) Title",
      },
    ],
    {
      id: "approvedTitle",
      type: "text",
      message: "Approver's Title",
    },
  ];

  return (
    <>
      <PopupModal
        header="Update Signatories"
        subHeader="Kindly update the signatory values"
        open={open}
        setOpen={setOpen}
        maxWidth="500px"
        zval={5}
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
            <FormGeneratorTemplate
              enableAutoFieldCheck
              fieldErrors={[]}
              template={Fields}
            />
          </FlexBox>
        </form>
        <FlexBox justifyContent="flex-end" marginTop="10px" gap="10px">
          <PrimaryButton
            label="Save"
            size="small"
            startIcon={<SaveIcon />}
            onClick={() => {
              updateSignatoriesCallback();
            }}
          />
        </FlexBox>
      </PopupModal>
    </>
  );
};

export default SignatoriesForm;
