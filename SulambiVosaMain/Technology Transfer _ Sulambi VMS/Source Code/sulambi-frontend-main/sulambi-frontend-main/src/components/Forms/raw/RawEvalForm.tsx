import { useContext } from "react";
import FlexBox from "../../FlexBox";
import FormGeneratorTemplate from "../FormGeneratorTemplate";
import { FormDataContext } from "../../../contexts/FormDataProvider";

const RawEvalForm = () => {
  const { formData, setFormData } = useContext(FormDataContext);

  return (
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
          viewOnly
          enableAutoFieldCheck
          fieldErrors={[]}
          template={[
            { type: "section", message: "Training/Seminar experience" },
            [
              {
                value: formData.criteria ? formData.criteria.overall ?? "" : "",
                type: "radiolist",
                message: "Overall, how would you rate the seminar/training?",
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
                value: formData.criteria
                  ? formData.criteria.appropriateness ?? ""
                  : "",
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
                value: formData.criteria
                  ? formData.criteria.expectations ?? ""
                  : "",
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
                value: formData.criteria ? formData.criteria.session ?? "" : "",
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
                value: formData.criteria ? formData.criteria.time ?? "" : "",
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
                value: formData.criteria
                  ? formData.criteria.materials ?? ""
                  : "",
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
                value: formData.criteria
                  ? formData.criteria.relevance ?? ""
                  : "",
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
                value: formData.criteria
                  ? formData.criteria.explained ?? ""
                  : "",
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
                value: formData.criteria
                  ? formData.criteria.learningEnvironment ?? ""
                  : "",
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
                value: formData.criteria
                  ? formData.criteria.timeManagement ?? ""
                  : "",
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
                value: formData.criteria
                  ? formData.criteria.keenness ?? ""
                  : "",
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
                value: formData.criteria ? formData.criteria.venue ?? "" : "",
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
              message: "Recommendations:",
            },
          ]}
        />
      </FlexBox>
    </form>
  );
};

export default RawEvalForm;
