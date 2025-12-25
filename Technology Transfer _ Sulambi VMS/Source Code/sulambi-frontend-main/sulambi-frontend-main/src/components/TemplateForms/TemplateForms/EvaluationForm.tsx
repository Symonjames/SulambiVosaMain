import { CSSProperties } from "react";
import BSUTemplateHeader from "./BSUTemplateHeader";
import ColSizeGen from "./ColSizeGen";

interface QuestionCheckboxRowProps {
  question: string;
  check?: number;
}

interface CriteriaRowProps {
  message: string[];
}

interface QuestionInputRowProps {
  question: string;
  answer?: string;
}

const criteriaStyle: CSSProperties = {
  // padding: "5px 5px",
  backgroundColor: "#c3c3c3",
  textAlign: "center",
  fontWeight: "bold",
};

const CriteriaRow: React.FC<CriteriaRowProps> = ({ message }) => {
  return (
    <tr>
      <td style={criteriaStyle} colSpan={10}>
        Criteria
      </td>
      <td style={criteriaStyle} colSpan={2}>
        5<br />
        <b style={{ fontSize: "10pt" }}>{message[0]}</b>
      </td>
      <td style={criteriaStyle} colSpan={2}>
        4<br />
        <b style={{ fontSize: "10pt" }}>{message[1]}</b>
      </td>
      <td style={criteriaStyle} colSpan={2}>
        3<br />
        <b style={{ fontSize: "10pt" }}>{message[2]}</b>
      </td>
      <td style={criteriaStyle} colSpan={2}>
        2<br />
        <b style={{ fontSize: "10pt" }}>{message[3]}</b>
      </td>
      <td style={criteriaStyle} colSpan={2}>
        1<br />
        <b style={{ fontSize: "10pt" }}>{message[4]}</b>
      </td>
    </tr>
  );
};

const QuestionCheckboxRow: React.FC<QuestionCheckboxRowProps> = ({
  question,
  check,
}) => {
  return (
    <tr>
      <td colSpan={10}>{question}</td>
      <td colSpan={2} style={{ textAlign: "center" }}>
        {check === 5 && "/"}
      </td>
      <td colSpan={2} style={{ textAlign: "center" }}>
        {check === 4 && "/"}
      </td>
      <td colSpan={2} style={{ textAlign: "center" }}>
        {check === 3 && "/"}
      </td>
      <td colSpan={2} style={{ textAlign: "center" }}>
        {check === 2 && "/"}
      </td>
      <td colSpan={2} style={{ textAlign: "center" }}>
        {check === 1 && "/"}
      </td>
    </tr>
  );
};

const QuestionInputRow: React.FC<QuestionInputRowProps> = ({
  question,
  answer,
}) => {
  return (
    <tr>
      <td colSpan={20}>
        {question}
        <br />
        {answer}
      </td>
    </tr>
  );
};

const EvaluationForm = () => {
  return (
    <BSUTemplateHeader formTitle="TRAINING / SEMINAR EVALUATION FORM">
      <table className="bsuFormChild">
        <ColSizeGen colSize={20} percentage="5%" />
        <tbody>
          <tr>
            <td colSpan={4}>Title of Training/Seminar:</td>
            <td colSpan={16}></td>
          </tr>
          <tr>
            <td colSpan={4}>Date:</td>
            <td colSpan={6}></td>
            <td colSpan={2}>Venue:</td>
            <td colSpan={8}></td>
          </tr>
          <tr>
            <td colSpan={20} style={{ fontSize: "10pt" }}>
              <b>Data Privacy Statement:</b> Pursuant to Republic Act No. 10173,
              also known as the Data Privacy Act of 2012, the Batangas State
              University, the National Engineering University, recognizes its
              commitment to protect and respect the privacy of its customers
              and/or stakeholders and ensure that all information collected from
              them are all processed in accordance with the principles of
              transparency, legitimate purpose and proportionality mandated
              under the Data Privacy Act of 2012.
              <br />
              <br />
              <b>Consent:</b> ☐ I have read this statement, understood its
              content, and consent to the processing of my personal data.
              <br />
              <br />
              Dear Participants,
              <br />
              <br />
              <u>
                Please evaluate the training/seminar in accordance with the
                criteria specified below. We assure you that your responses will
                be kept in strict confidentiality.
              </u>
            </td>
          </tr>
          <tr>
            <td colSpan={4}>
              Name (<i>optional</i>):
            </td>
            <td colSpan={4}></td>
            <td colSpan={2}>Age:</td>
            <td colSpan={4}></td>
            <td colSpan={2}>Sex</td>
            <td colSpan={4}></td>
          </tr>
          <tr>
            <td colSpan={4}>Email Address:</td>
            <td colSpan={16}></td>
          </tr>
          <tr>
            <td colSpan={4}>Organization/Affiliation:</td>
            <td colSpan={6}></td>
            <td colSpan={2}>Position/ Designation:</td>
            <td colSpan={8}></td>
          </tr>
          <tr>
            <td colSpan={7}>
              <i style={{ fontSize: "10pt" }}>
                (For BatStateU Faculty/Employee only)
              </i>{" "}
              Campus:
            </td>
            <td colSpan={3}></td>
            <td colSpan={2}>Rank:</td>
            <td colSpan={8}></td>
          </tr>
          <tr>
            <td colSpan={20}>
              <u>
                Please check the column corresponding to your response for each
                of the statements below.
              </u>
            </td>
          </tr>

          <CriteriaRow
            message={[
              "Excellent",
              "Very Satisfactory",
              "Satisfactory",
              "Fair",
              "Poor",
            ]}
          />
          <QuestionCheckboxRow question="1. Overall, how would you rate the seminar/training?" />
          <QuestionCheckboxRow
            question="2. How would you rate the appropriateness of time and the proper
              use of resources provided?"
          />

          <CriteriaRow
            message={[
              "Outstanding",
              "Very Satisfactory",
              "Satisfactory",
              "Unsatisfactory",
              "Poor",
            ]}
          />
          <QuestionCheckboxRow question="3. Objectives and expectations were clearly communicated and achieved." />
          <QuestionCheckboxRow question="4. Session activities were appropriate and relevant to the achievement of the learning objectives." />
          <QuestionCheckboxRow question="5. Sufficient time was allotted for group discussion and comments." />
          <QuestionCheckboxRow question="6. Materials and audio-visual aids provided were useful." />
          <QuestionCheckboxRow question="7. The resource person/trainer displayed thorough knowledge of, and provided relevant insights on the topic/s discussed." />
          <QuestionCheckboxRow question="8. The resource person/trainer thoroughly explained and processed the learning activities throughout the training." />
          <QuestionCheckboxRow question="9. The resource person/trainer created a good learning environment, sustained the attention of the participants, and encouraged their participation in the training duration." />
          <QuestionCheckboxRow question="10. The resource person/trainer managed the time well, including some adjustments in the training schedule, if needed." />
          <QuestionCheckboxRow question="11. The resource person/trainer demonstrated keenness to the participants' needs and other requirements related to the training." />
          <QuestionCheckboxRow question="13. The venue or platform used was conducive for learning." />
          <QuestionInputRow question="13. Was the training helpful for you in the practice of your profession? Why or why not?" />
          <QuestionInputRow question="14. What aspect of the training has been helpful to you? What other topics would you suggest for future trainings?" />
          <QuestionInputRow question="15. Comments/Commendations/Complaints:" />
          <tr>
            <td colSpan={20} style={{ textAlign: "center" }}>
              Thank You!
            </td>
          </tr>
        </tbody>
      </table>
    </BSUTemplateHeader>
  );
};

export default EvaluationForm;
