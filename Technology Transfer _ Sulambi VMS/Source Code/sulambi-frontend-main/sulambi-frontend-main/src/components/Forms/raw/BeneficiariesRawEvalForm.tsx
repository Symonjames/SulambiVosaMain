import { useContext } from "react";
import FlexBox from "../../FlexBox";
import FormGeneratorTemplate from "../FormGeneratorTemplate";
import { FormDataContext } from "../../../contexts/FormDataProvider";

interface Props {
  eventData?: {
    title?: string;
    date?: string;
    venue?: string;
  };
  viewOnly?: boolean;
}

const BeneficiariesRawEvalForm = ({ eventData, viewOnly = false }: Props) => {
  const { formData, setFormData } = useContext(FormDataContext);

  return (
    <form
      style={{
        width: "100%",
      }}
    >
      <FlexBox
        flexDirection="column"
        alignItems="center"
        marginBottom="20px"
        rowGap="15px"
      >
        <FormGeneratorTemplate
          viewOnly={viewOnly}
          enableAutoFieldCheck
          fieldErrors={[]}
          template={[
            { type: "section", message: "BENEFICIARY EVALUATION FORM" },
            ...(eventData
              ? [
                  {
                    type: "label",
                    message: `Title of Service/Program: ${eventData.title}`,
                  },
                  {
                    type: "label",
                    message: `Date: ${eventData.date}`,
                  },
                  {
                    type: "label",
                    message: `Location: ${eventData.venue}`,
                  },
                ]
              : [
                  {
                    id: "trainingTitle",
                    type: "text",
                    message: "Title of Service/Program:",
                    required: true,
                  },
                  {
                    id: "trainingDate",
                    type: "date",
                    message: "Date:",
                    required: true,
                  },
                  {
                    id: "venue",
                    type: "text",
                    message: "Location:",
                    required: true,
                  },
                ]),
            { type: "section", message: "Data Privacy Statement" },
            {
              type: "label",
              message: "Pursuant to Republic Act No. 10173, also known as the Data Privacy Act of 2012, the Batangas State University, the National Engineering University, recognizes its commitment to protect and respect the privacy of its customers and/or stakeholders and ensure that all information collected from them are all processed in accordance with the principles of transparency, legitimate purpose and proportionality mandated under the Data Privacy Act of 2012."
            },
            {
              type: "label",
              message: "Dear Service Recipients,\n\nPlease evaluate the community service you received in accordance with the criteria specified below. We assure you that your responses will be kept in strict confidentiality."
            },
            { type: "section", message: "Beneficiary Experience Evaluation" },
            [
              {
                value: formData.criteria ? formData.criteria.overall ?? "" : "",
                type: "radiolist",
                message: "Overall, how would you rate your volunteer experience?",
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
                  "How would you rate the organization and support provided during the volunteer activity?",
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
                  "Were your volunteer expectations clearly communicated and met?",
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
                  "Were the volunteer activities meaningful and relevant to the community needs?",
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
                  "Was there sufficient time allocated for volunteer activities and interaction with beneficiaries?",
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
                  "Were the materials, resources, and tools provided adequate for volunteer activities?",
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
                  "Did the volunteer coordinators demonstrate good knowledge and provided relevant guidance?",
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
                  "Were the volunteer tasks and procedures clearly explained and demonstrated?",
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
                  "Was the volunteer environment welcoming and conducive for meaningful participation?",
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
                  "Was the volunteer schedule well-managed with appropriate breaks and adjustments when needed?",
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
                  "Did the volunteer coordinators show attentiveness to volunteer needs and concerns?",
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
                  "Was the volunteer venue or location suitable and safe for volunteer activities?",
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
              message: "Beneficiary Feedback & Suggestions",
            },
            {
              id: "q13",
              type: "textQuestion",
              message:
                "Was this volunteer experience meaningful and impactful for you? Why or why not?",
            },
            {
              id: "q14",
              type: "textQuestion",
              message:
                "What skills did you develop or improve through this volunteer experience? What other volunteer opportunities would you suggest?",
            },
            {
              id: "comment",
              type: "textQuestion",
              message: "Comments/Commendations/Complaints:",
            },
            {
              id: "recommendations",
              type: "textQuestion",
              message: "Recommendations for improving future volunteer programs:",
            },
          ]}
        />
      </FlexBox>
    </form>
  );
};

export default BeneficiariesRawEvalForm;