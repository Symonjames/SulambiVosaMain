import { ReactNode, useContext, useState } from "react";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import SendIcon from "@mui/icons-material/Send";
import PrimaryButton from "../Buttons/PrimaryButton";
import FormGeneratorTemplate, {
  FormGenTemplateProps,
} from "./FormGeneratorTemplate";
import { createNewAccount } from "../../api/accounts";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

interface Props {
  accountType: "officer" | "admin";
  open?: boolean;
  componentsBeforeSubmit?: ReactNode;
  hideSubmit?: boolean;
  setOpen?: (state: boolean) => void;
  onSubmit?: () => void;
}

const AccountsForm: React.FC<Props> = (props) => {
  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);

  const {
    accountType,
    componentsBeforeSubmit,
    hideSubmit,
    open,
    onSubmit,
    setOpen,
  } = props;

  const [disableButton, setDisableButton] = useState(false);
  const [fieldErrors, setFieldErrors] = useState([]);

  const createAccount = () => {
    setDisableButton(true);
    createNewAccount(accountType, formData)
      .then(() => {
        showSnackbarMessage("Successfully created new account", "success");
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
      .finally(() => {
        setOpen && setOpen(false);
        onSubmit && onSubmit();
        setFormData({});
      });
  };

  const FormContent: (FormGenTemplateProps | FormGenTemplateProps[])[] = [
    [
      { id: "username", type: "text", message: "Username" },
      { id: "password", type: "text", message: "Password" },
    ],
  ];

  return (
    <PopupModal
      open={!!open}
      setOpen={setOpen}
      header="Manage Account"
      subHeader="Kindly fillup the required form data below"
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
            fieldErrors={fieldErrors}
            template={FormContent}
            enableAutoFieldCheck
          />
        </FlexBox>
      </form>
      <FlexBox justifyContent="flex-end" marginTop="10px" gap="10px">
        {componentsBeforeSubmit}
        {!hideSubmit && (
          <PrimaryButton
            label="Submit"
            size="small"
            icon={<SendIcon />}
            disabled={disableButton}
            onClick={() => {
              createAccount();
            }}
          />
        )}
      </FlexBox>
    </PopupModal>
  );
};

export default AccountsForm;
