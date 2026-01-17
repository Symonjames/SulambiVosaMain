import { useCallback, useContext, useEffect, useState } from "react";
import PrimaryButton from "../components/Buttons/PrimaryButton";
import FlexBox from "../components/FlexBox";
import FormGeneratorTemplate from "../components/Forms/FormGeneratorTemplate";
import PopupModal from "../components/Modal/PopupModal";
import SendIcon from "@mui/icons-material/Send";
import { useNavigate, useParams } from "react-router-dom";
import TextHeader from "../components/Headers/TextHeader";
import { FormDataContext } from "../contexts/FormDataProvider";
import { checkReqIdValidity, createEvaluation } from "../api/evaluation";
import { IconButton, Typography } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { SnackbarContext } from "../contexts/SnackbarProvider";
import { useMediaQuery } from "react-responsive";

const PublicForm = () => {
  const isMobile = useMediaQuery({
    query: "(max-width: 1224px)",
  });

  const { showSnackbarMessage } = useContext(SnackbarContext);
  const [disableButton, setDisableButton] = useState(false);
  const [isIdValid, setIsIdValid] = useState<boolean | undefined>(undefined);
  const [canSubmit, setCanSubmit] = useState(true);
  const [alreadySubmitted, setAlreadySubmitted] = useState(false);
  const [fieldErrors, setFieldErrors] = useState([]);

  const { formData, setFormData } = useContext(FormDataContext);
  const { id } = useParams();

  const navigate = useNavigate();

  useEffect(() => {
    (async function () {
      if (id) {
        try {
          const response = await checkReqIdValidity(id);
          setIsIdValid(true);
          setCanSubmit(response.data?.canSubmit ?? true);
          setAlreadySubmitted(response.data?.alreadySubmitted ?? false);
        } catch (err: any) {
          setIsIdValid(false);
          if (err.response?.data?.message) {
            showSnackbarMessage(err.response.data.message, "error");
          }
        }
      }
    })();
  }, [id]);

  useEffect(() => {
    setFormData({
      criteria: {},
    });
  }, []);

  const submitCallback = useCallback(async () => {
    if (id) {
      try {
        await createEvaluation(id, formData);
        // Dispatch event to refresh satisfaction analytics chart
        window.dispatchEvent(new CustomEvent('satisfaction-rating-submitted'));
        navigate("/feedback-message");
      } catch (err: any) {
        if (err.response.data) {
          const message = err.response.data.message;
          const errors = err.response.data.fieldError ?? [];

          setFieldErrors(errors);
          showSnackbarMessage(`Error Occured: ${message}`, "error");
        }
      } finally {
        setDisableButton(false);
      }
    }
  }, [formData]);

  return (
    <FlexBox
      minHeight="100vh"
      width="100%"
      justifyContent="center"
      alignItems="center"
      bgcolor="white"
      sx={{
        background: "linear-gradient(180deg, #c07f00 0%, #ffdf75 100%)",
      }}
    >
      {isIdValid === true ? (
        <>
          <PopupModal
            open
            hideCloseButton
            disableBGShadow
            width={isMobile ? "100vw" : "60vw"}
            minHeight="90vh"
            maxHeight="90vh"
            header="Evaluation modal"
            subHeader={alreadySubmitted ? "Evaluation form has already been submitted" : "Kindly answer the evaluation form below"}
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
                  enableAutoFieldCheck
                  fieldErrors={fieldErrors}
                  template={[
                    {
                      type: "divider",
                    },
                    [
                      {
                        type: "label",
                        message:
                          "Welcome to Our Event Evaluation! Thank you for joining us the event! Your feedback is incredibly valuable to us and will help us improve future events. Please take a moment to share your thoughts and experiences by completing this evaluation form. Your insights will contribute to making our events even better. We appreciate your time and input!",
                      },
                    ],
                    { type: "section", message: "Training/Seminar experience" },
                    [
                      {
                        type: "radiolist",
                        message:
                          "Overall, how would you rate the seminar/training?",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              overall: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "How would you rate the appropriateness of time and the proper use of resources provided?",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              appropriateness: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "Objectives and expectations were clearly communicated and achieved.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              expectations: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "Session activities were appropriate and relevant to the achievement of the learning objectives.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              session: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "Sufficient time was allotted for group discussion and comments.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              time: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "Materials and audio-visual aids provided were useful.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              materials: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "The resource person/trainer displayed thorough knowledge of, and provided relevant insights on the topic/s discussed.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              relevance: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "The resource person/trainer thoroughly explained and processed the learning activities throughout the training.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              explained: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "The resource person/trainer created a good learning environment, sustained the attention of the participants, and encouraged their participation in the training duration.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              learningEnvironment: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "The resource person/trainer managed the time well, including some adjustments in the training schedule, if needed.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              timeManagement: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "The resource person/trainer demonstrated keenness to the participants' needs and other requirements related to the training.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              keenness: value,
                            },
                          });
                        },
                      },
                    ],
                    [
                      {
                        type: "radiolist",
                        message:
                          "The venue or platform used was conducive for learning.",
                        radioListRowDirection: true,
                        selectionQuestion: [
                          { label: "Excellent", initialValue: false },
                          { label: "Very Satisfactory", initialValue: false },
                          { label: "Satisfactory", initialValue: false },
                          { label: "Fair", initialValue: false },
                          { label: "Poor", initialValue: false },
                        ],
                        onUse: (value: any) => {
                          setFormData({
                            ...formData,
                            criteria: {
                              ...formData.criteria,
                              venue: value,
                            },
                          });
                        },
                      },
                    ],
                    {
                      type: "section",
                      message: "Comments / Suggestions / Complaint",
                    },
                    {
                      id: "q13",
                      type: "textQuestion",
                      message:
                        "Was the training helpful for you in the practice of your profession? Why or why not?",
                    },
                    {
                      id: "q14",
                      type: "textQuestion",
                      message:
                        "What aspect of the training has been helpful to you? What other topics would you suggest for future trainings?",
                    },
                    {
                      id: "comment",
                      type: "textQuestion",
                      message: "Comments/Commendations/Complaints:",
                    },
                    {
                      id: "recommendations",
                      type: "textQuestion",
                      message:
                        "What topic for future events do you want recommend?",
                    },
                  ]}
                />
              </FlexBox>
            </form>
            <FlexBox justifyContent="flex-end" marginTop="20px">
              {alreadySubmitted ? (
                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                  This evaluation has already been submitted. Thank you for your feedback!
                </Typography>
              ) : (
                <PrimaryButton
                  label="Submit"
                  size="small"
                  icon={<SendIcon />}
                  disabled={disableButton || !canSubmit}
                  onClick={() => {
                    setDisableButton(true);
                    submitCallback();
                  }}
                />
              )}
            </FlexBox>
          </PopupModal>
        </>
      ) : (
        <>
          <IconButton
            sx={{ position: "fixed", top: "20px", left: "20px" }}
            onClick={() => navigate("/")}
          >
            <ArrowBackIcon />
          </IconButton>

          <TextHeader textAlign={"center"}>
            The evaluation ID provided is not valid
          </TextHeader>
        </>
      )}
    </FlexBox>
  );
};

export default PublicForm;
