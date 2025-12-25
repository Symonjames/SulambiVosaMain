import PrimaryButton from "../Buttons/PrimaryButton";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import SendIcon from "@mui/icons-material/Send";
import FormGeneratorTemplate, {
  FormGenTemplateProps,
} from "./FormGeneratorTemplate";
import {
  getEventFeedback,
  submitFeedback,
  updateFeedback,
} from "../../api/feedback";
import { useContext, useEffect } from "react";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { SnackbarContext } from "../../contexts/SnackbarProvider";
import { AxiosError } from "axios";

interface Props {
  eventId?: number;
  eventType?: "external" | "internal";
  feedbackId?: number;
  viewOnly?: boolean;
  open: boolean;
  setOpen: (state: boolean) => void;
  onClose?: () => void;
}

const FeedbackForm: React.FC<Props> = ({
  eventId,
  eventType,
  feedbackId,
  viewOnly,
  open,
  setOpen,
  onClose,
}) => {
  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);

  useEffect(() => {
    (async function () {
      if (!!feedbackId && !!eventType && !!eventId) {
        try {
          const response = await getEventFeedback(eventType, eventId);
          setFormData({ feedback: response.data.message });
        } catch (error: AxiosError | any) {
          let errmsg = null;
          if (error?.response?.data?.message)
            errmsg = error?.response?.data?.message;
          showSnackbarMessage(
            errmsg ?? "An error occured in fetching feedback",
            "error"
          );
          console.error(error);
        }
      }
    })();
  }, [feedbackId, eventType, eventId]);

  const feedbackForm: (FormGenTemplateProps | FormGenTemplateProps[])[] = [
    {
      type: "textQuestion",
      id: "feedback",
      message: viewOnly ? "" : "Enter Feedback for the Event",
      required: !viewOnly,
    },
  ];

  const postFeedback = async () => {
    if (feedbackId && feedbackId !== null) {
      try {
        updateFeedback(feedbackId, formData.feedback ?? "");
        showSnackbarMessage("Feedback updated successfully", "success");
        setOpen(false);
      } catch (error: AxiosError | any) {
        let errmsg = null;
        if (error?.response?.data?.message)
          errmsg = error?.response?.data?.message;
        showSnackbarMessage(
          errmsg ?? "An error occured in updating feedback",
          "error"
        );
        console.error(error);
      }
      return;
    }

    if (eventId && eventType) {
      try {
        await submitFeedback(eventType, eventId, formData.feedback ?? "");
        showSnackbarMessage("Feedback submitted successfully", "success");
        setOpen(false);
      } catch (error: AxiosError | any) {
        let errmsg = null;
        if (error?.response?.data?.message)
          errmsg = error?.response?.data?.message;
        showSnackbarMessage(
          errmsg ?? "An error occured in submitting feedback",
          "error"
        );
        console.error(error);
      }
      return;
    }
  };

  return (
    <PopupModal
      open={!!open}
      onClose={onClose}
      setOpen={setOpen}
      header="Event Feedback form"
      subHeader={
        viewOnly
          ? "Kindly evaluate the feedback below"
          : "Kindly fillup the required form data below"
      }
      zval={6}
    >
      <form
        style={{
          maxHeight: "75vh",
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
            enableAutoFieldCheck={true}
            fieldErrors={[]}
            viewOnly={viewOnly}
            template={feedbackForm}
          />
        </FlexBox>
      </form>
      {!viewOnly && (
        <FlexBox justifyContent="flex-end" marginTop="10px" gap="10px">
          <PrimaryButton
            label="Submit"
            size="small"
            icon={<SendIcon />}
            onClick={() => {
              postFeedback();
              setFormData({});
              onClose && onClose();
            }}
          />
        </FlexBox>
      )}
    </PopupModal>
  );
};

export default FeedbackForm;
