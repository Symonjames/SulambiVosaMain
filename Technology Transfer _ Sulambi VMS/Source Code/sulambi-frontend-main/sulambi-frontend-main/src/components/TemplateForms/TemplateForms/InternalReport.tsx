import dayjs from "dayjs";
import {
  InternalReportAnalytics,
  InternalReportType,
} from "../../../interface/types";
import BSUTemplateHeader from "./BSUTemplateHeader";
import ColSizeGen from "./ColSizeGen";
import { useEffect, useState } from "react";
import { getReportAnalytics } from "../../../api/reports";
import BSUTemplateSigning from "./BSUTemplateSigning";
import FlexBox from "../../FlexBox";
import { CheckBoxText, RomanListValues } from "./ExternalEventForm";
import AdminPhotoDisplay from "./AdminPhotoDisplay";
import SafeHtmlRenderer from "../../Inputs/SafeHtmlRenderer";
import { stripLeadingRoman } from "../../../utils/stripLeadingRoman";
import { InnerFormTableTemplate } from "./InternalEventForm";

interface Props {
  data: InternalReportType;
  textAlign?: "left" | "justify";
}

const InternalReport: React.FC<Props> = ({ data, textAlign }) => {
  const [reportAnalytics, setReportAnalytics] =
    useState<InternalReportAnalytics>();
  const [financialRequirement, setFinancialRequirement] = useState<any>({});
  const [evaluationMechanicsPlan, setEvaluationMechanicsPlan] = useState<any>({});

  const safeParseJsonObject = (raw: any): any => {
    if (!raw) return {};
    if (typeof raw === "object") return raw;
    if (typeof raw !== "string") return {};
    try {
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch {
      return {};
    }
  };

  useEffect(() => {
    if (data && data.eventId && data.eventId.id)
      getReportAnalytics(data.eventId.id, "internal").then((response) => {
        setReportAnalytics(response.data.data);
      });
    setFinancialRequirement(safeParseJsonObject(data?.eventId?.financialRequirement));
    setEvaluationMechanicsPlan(safeParseJsonObject(data?.eventId?.evaluationMechanicsPlan));
  }, [data]);

  return (
    <BSUTemplateHeader
      formTitle="NARRATIVE REPORT (INTERNAL GAD PROGRAM/PROJECT/ACTIVITY)"
      reference="Reference No.: BatStateU-FO-ESO-10"
      effectivityDate="Effectivity Date: August 25, 2023"
      revisionNumber="Revision No.: 00"
      romaize
    >
      <table className="bsuFormChild" style={{ marginTop: 0, borderTop: "none", borderSpacing: 0 }}>
        <ColSizeGen colSize={2} percentage="50%" />
        <tbody>
          <tr>
            <td colSpan={2} className="fontSet">
              <FlexBox justifyContent="space-around">
                <CheckBoxText
                  romaize
                  message="Program"
                  checked={
                    data?.eventId?.eventProposalType?.includes("Program") ??
                    false
                  }
                />
                <CheckBoxText
                  romaize
                  message="Project"
                  checked={
                    data?.eventId?.eventProposalType?.includes("Project") ??
                    false
                  }
                />
                <CheckBoxText
                  romaize
                  message="Activity"
                  checked={
                    data?.eventId?.eventProposalType?.includes("Activity") ??
                    false
                  }
                />
              </FlexBox>
            </td>
          </tr>
          <tr>
            <td colSpan={2} className="fontSet">
              <RomanListValues
                romaize
                marginBetween="10px"
                list={[
                  { title: "Title: ", value: stripLeadingRoman(data?.eventId?.title) },
                  {
                    title: "Date and Venue: ",
                    value: stripLeadingRoman(
                      `${data?.eventId?.venue} (${dayjs(data?.eventId?.durationStart).format(
                        "MMMM D, YYYY h:mm A"
                      )} - ${dayjs(data?.eventId?.durationEnd).format(
                        "MMMM D, YYYY h:mm A"
                      )})`
                    ),
                  },
                  {
                    title: "Mode of delivery (online/face-to-face): ",
                    value: stripLeadingRoman(data?.eventId?.modeOfDelivery),
                  },
                  {
                    title: "Project Team: ",
                    value: stripLeadingRoman(data?.eventId?.projectTeam),
                  },
                  {
                    title: "Partner Office/College/Department: ",
                    value: stripLeadingRoman(data?.eventId?.partner),
                  },
                  {
                    title: "Type of Participants: ",
                    value: (
                      <span
                        style={{
                          borderBottom: "1px solid #000",
                          display: "inline-block",
                          minWidth: "200px",
                          paddingBottom: "1px",
                        }}
                      >
                        {stripLeadingRoman(data?.eventId?.participant) || "\u00A0"}
                      </span>
                    ),
                  },
                ]}
              />
              <br />
              {/* --- Type of Participants Table (small + centered like InternalEventForm) --- */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  width: "35%",
                  marginTop: "2px",
                  marginBottom: "2px",
                  marginLeft: "auto",
                  marginRight: "auto",
                }}
              >
                <table
                  className="participant-table bsuFormChild"
                  style={{
                    width: "100%",
                    fontSize: "10pt",
                    borderCollapse: "collapse",
                    borderSpacing: 0,
                    tableLayout: "fixed",
                    background: "#fff",
                    outline: "none",
                  }}
                >
                  <colgroup>
                    <col style={{ width: "50%" }} />
                    <col style={{ width: "50%" }} />
                  </colgroup>

                  <tbody>
                    {/* top header row */}
                    <tr>
                      <td
                        style={{
                          padding: "2px 4px",
                          textAlign: "center",
                        }}
                      ></td>
                      <td
                        style={{
                          padding: "2px 4px",
                          textAlign: "center",
                          fontWeight: 600,
                        }}
                      >
                        Total
                      </td>
                    </tr>

                    {/* male row */}
                    <tr>
                      <td
                        style={{
                          padding: "2px 4px",
                          textAlign: "center",
                        }}
                      >
                        Male
                      </td>
                      <td
                        style={{
                          padding: "2px 4px",
                          textAlign: "center",
                        }}
                      >
                        {reportAnalytics?.sex?.male ?? 0}
                      </td>
                    </tr>

                    {/* female row */}
                    <tr>
                      <td
                        style={{
                          padding: "2px 4px",
                          textAlign: "center",
                        }}
                      >
                        Female
                      </td>
                      <td
                        style={{
                          padding: "2px 4px",
                          textAlign: "center",
                        }}
                      >
                        {reportAnalytics?.sex?.female ?? 0}
                      </td>
                    </tr>

                    {/* total row */}
                    <tr>
                      <td
                        style={{
                          padding: "2px 4px",
                          fontWeight: 600,
                          textAlign: "center",
                        }}
                      >
                        Total
                      </td>
                      <td
                        style={{
                          padding: "2px 4px",
                          textAlign: "center",
                          fontWeight: 600,
                        }}
                      >
                        {(reportAnalytics?.sex?.male ?? 0) + (reportAnalytics?.sex?.female ?? 0)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <RomanListValues
                romaize
                marginBetween="10px"
                start={7}
                list={[
                  {
                    title: "Objectives: ",
                    value: stripLeadingRoman(data?.eventId?.objectives),
                    newlineAfterValue: true,
                  },
                  {
                    title: "Evaluation Results: ",
                  },
                ]}
              />
              <br />
              {/* --- Evaluation Results as InnerFormTableTemplate (replace old table) --- */}
              <div style={{ width: "90%", margin: "0 auto" }}>
                {(() => {
                  const er = reportAnalytics?.evalResult;
                  const male = er?.male || {
                    excellent: 0,
                    verySatisfactory: 0,
                    satisfactory: 0,
                    fair: 0,
                    poor: 0,
                  };
                  const female = er?.female || {
                    excellent: 0,
                    verySatisfactory: 0,
                    satisfactory: 0,
                    fair: 0,
                    poor: 0,
                  };
                  const rows = [
                    {
                      code: "2.1",
                      scale: "Excellent",
                      male: male.excellent ?? 0,
                      female: female.excellent ?? 0,
                      preferNot: 0,
                      total: (Number(male.excellent ?? 0) + Number(female.excellent ?? 0)),
                    },
                    {
                      code: "2.2",
                      scale: "Very Satisfactory",
                      male: male.verySatisfactory ?? 0,
                      female: female.verySatisfactory ?? 0,
                      preferNot: 0,
                      total: (Number(male.verySatisfactory ?? 0) + Number(female.verySatisfactory ?? 0)),
                    },
                    {
                      code: "2.3",
                      scale: "Satisfactory",
                      male: male.satisfactory ?? 0,
                      female: female.satisfactory ?? 0,
                      preferNot: 0,
                      total: (Number(male.satisfactory ?? 0) + Number(female.satisfactory ?? 0)),
                    },
                    {
                      code: "2.4",
                      scale: "Fair",
                      male: male.fair ?? 0,
                      female: female.fair ?? 0,
                      preferNot: 0,
                      total: (Number(male.fair ?? 0) + Number(female.fair ?? 0)),
                    },
                    {
                      code: "2.5",
                      scale: "Poor",
                      male: male.poor ?? 0,
                      female: female.poor ?? 0,
                      preferNot: 0,
                      total: (Number(male.poor ?? 0) + Number(female.poor ?? 0)),
                    },
                  ];
                  const header = ["", "Scale", "Male", "Female", "Prefer Not to say", "Total"];
                  const dataKeys = ["code", "scale", "male", "female", "preferNot", "total"];
                  return (
                    <InnerFormTableTemplate
                      textAlign="center"
                      customColsize={6}
                      customFlexSize={[0.8, 1.5, 0.8, 0.8, 0.8, 0.8]}
                      header={header}
                      dataKeys={dataKeys}
                      data={rows}
                    />
                  );
                })()}
              </div>
              <RomanListValues
                romaize
                marginBetween="10px"
                start={9}
                list={[
                  {
                    title: "Narrative of the Project/Activity: ",
                    newlineAfterValue: true,
                    value: (
                      <SafeHtmlRenderer
                        htmlContent={data?.narrative || ""}
                        style={{ textAlign }}
                      />
                    ),
                  },
                ]}
              />
              <br />
              <RomanListValues
                romaize
                marginBetween="10px"
                start={10}
                list={[
                  {
                    title: "Financial Requirements and Source of Funds: ",
                  },
                ]}
              />
              <div style={{ width: "90%", margin: "0 auto" }}>
                <InnerFormTableTemplate
                  textAlign="center"
                  customColsize={7}
                  customFlexSize={[3]}
                  header={[
                    "Item Description",
                    "Quantity",
                    "Unit",
                    "Unit Cost",
                    "Total",
                  ]}
                  dataKeys={["item", "qty", "unit", "unitCost", "total"]}
                  data={Object.keys(financialRequirement).map((index) => {
                    return financialRequirement[index];
                  })}
                />
              </div>
              <div className="monitoring-evaluation-section">
                <div className="monitoring-evaluation-title">
                  <RomanListValues
                    romaize
                    marginBetween="0px"
                    start={11}
                    list={[
                      {
                        title: "Monitoring and Evaluation Mechanics / Plan: ",
                      },
                    ]}
                  />
                </div>
                <div className="inner-form-table" style={{ width: "90%", margin: "6px auto 0 auto" }}>
                  <InnerFormTableTemplate
                    textAlign="center"
                    header={[
                      "Objectives",
                      "Performance Indicators",
                      "Baseline Data",
                      "Performance Target",
                      "Data Source",
                      "Collection Method",
                      "Frequency of Data Collection",
                      "Office/Persons Responsible",
                    ]}
                    dataKeys={[
                      "specificObjective",
                      "performanceIndicator",
                      "baselineData",
                      "performanceTarget",
                      "dataSource",
                      "collectionMethod",
                      "frequencyOfCollection",
                      "personResponsible",
                    ]}
                    data={Object.keys(evaluationMechanicsPlan).map((index) => {
                      return evaluationMechanicsPlan[index];
                    })}
                  />
                </div>
              </div>
              <RomanListValues
                romaize
                marginBetween="10px"
                start={12}
                list={[
                  {
                    title: "Photos: ",
                  },
                ]}
              />
              <br />
              <AdminPhotoDisplay
                photos={data?.photos || []}
                captions={data?.photoCaptions || []}
                maxPhotos={2}
              />
            </td>
          </tr>
          <tr>
            <BSUTemplateSigning
              colspan={1}
              upperMessage="Prepared By:"
              designation={data?.signatoriesId?.preparedTitle}
              placeHolder={data?.signatoriesId?.preparedBy}
              romaize
            />
            <BSUTemplateSigning
              colspan={1}
              upperMessage="Reviewed By:"
              designation={data?.signatoriesId?.reviewedTitle}
              placeHolder={data?.signatoriesId?.reviewedBy}
              romaize
            />
          </tr>
          <tr>
            <BSUTemplateSigning
              colspan={2}
              upperMessage="Approved By:"
              designation={data?.signatoriesId?.approvedTitle}
              placeHolder={data?.signatoriesId?.approvedBy}
              romaize
            />
          </tr>
        </tbody>
      </table>
      <div className="fontSet" style={{ marginTop: "10px", fontSize: "10pt", fontFamily: "'Times New Roman', serif", fontStyle: "italic" }}>
        Cc: GAD Central
      </div>
    </BSUTemplateHeader>
  );
};

export default InternalReport;
