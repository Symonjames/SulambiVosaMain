import { useEffect, useState } from "react";
import { ExternalReportType, ReportAnalytics } from "../../../interface/types";
import BSUTemplateHeader from "./BSUTemplateHeader";
import ColSizeGen from "./ColSizeGen";
import dayjs from "dayjs";
import { getReportAnalytics } from "../../../api/reports";
import BSUTemplateSigning from "./BSUTemplateSigning";
import AdminPhotoDisplay from "./AdminPhotoDisplay";
import SafeHtmlRenderer from "../../Inputs/SafeHtmlRenderer";
import { PreviewCheckbox } from "./ExternalEventForm";

interface Props {
  data: ExternalReportType;
  textAlign?: "left" | "justify";
}


const ExternalReport: React.FC<Props> = ({ data, textAlign }) => {
  const [reportAnalytics, setReportAnalytics] = useState<ReportAnalytics>();

  const insensitiveCaseCheck = (sourceList: string, value: string) => {
    let lst = [];
    try {
      lst = JSON.parse(sourceList);
    } catch (err) {
      lst = [];
    }
    for (let i = 0; i < lst.length; i++) {
      if (value === lst[i]) {
        return true;
      }
    }
    return false;
  };

  const sdgList = [
    "No Poverty",
    "Zero Hunger",
    "Good Health and Well-Being",
    "Quality Education",
    "Gender Equality",
    "Clean Water and Sanitation",
    "Affordable and Clean Energy",
    "Decent Work and Economic Growth",
    "Industry, Innovation and Infrastructure",
    "Reduced Inequalities",
    "Sustainable Cities and Communities",
    "Responsible Consumption and Production",
    "Climate Action",
    "Life Below Water",
    "Life on Land",
    "Peace, Justice and Strong Institutions",
    "Partnerships for the Goals",
  ];

  const extensionServiceList = [
    "BatStateU Inclusive Social Innovation for Regional Growth (BISIG) Program",
    "Livelihood and other Entrepreneurship related on Agri-Fisheries (LEAF)",
    "Environment and Natural Resources Conservation, Protection, and Rehabilitation Program",
    "SMART Analytics and Engineering Innovation",
    "Adopt-a-Municipality/Barangay/School/Social Development Thru BIDANI Implementation",
    "Community Outreach",
    "Technical-Vocational Education and Training (TVET) Program",
    "Technology Transfer and Adoption/Utilization Program",
    "Technical Assistance and Advisory Services Program",
    "Parents’ Empowerment through Social Development (PESODEV)",
    "Gender and Development",
    "Disaster Risk Reduction and Management and Disaster Preparedness and Response/Climate Change Adaptation (DRRM and DPR/CCA)",
  ];

  useEffect(() => {
    if (data && data?.eventId && data?.eventId?.id)
      getReportAnalytics(data.eventId.id, "external").then((response) => {
        setReportAnalytics(response.data.data);
      });
  }, [data]);

  return (
    <BSUTemplateHeader
      romaize
      reference="Reference No.: BatStateU-REC-ESO-03"
      effectivityDate="Effectivity Date: August 25, 2023"
      revisionNumber="Revision No.: 04"
    >
      <table className="bsuFormChild">
        <ColSizeGen colSize={10} percentage="10%" />
        <tbody>
          <tr>
            <td colSpan={1} className="fontSet" style={{ textAlign: "center" }}>
              Title
            </td>
            <td
              colSpan={9}
              className="fontSet"
              style={{ textAlign: "center", fontWeight: "bold" }}
            >
              EXTENSION PROJECT / ACTIVITY EVALUATION REPORT
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Title of the Project or Activity:
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {data?.eventId?.title}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Location:
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {data?.eventId?.location}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Duration : (Date of Implementation / Number of hours of
              implementation):
            </td>
            <td colSpan={7} className="fontSet">
              {data?.eventId?.durationStart
                ? dayjs(data.eventId.durationStart).format(
                    "MMMM D, YYYY h:mm A"
                  )
                : ""}
              {" - "}
              {data?.eventId?.durationEnd
                ? dayjs(data.eventId.durationStart).format(
                    "MMMM D, YYYY h:mm A"
                  )
                : ""}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Implementing Office/ College / Organization / Program (specify the
              programs under the college implementing the project):
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {data?.eventId?.orgInvolved}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Partner Agency:
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {data?.eventId?.partners}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Type of Extension Service Agenda: Choose the MOST (only one)
              applicable Extension Agenda from the following:
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {extensionServiceList.map((extensionType, index) => {
                return (
                  <ul key={index}>
                    {" "}
                    <PreviewCheckbox
                      checked={insensitiveCaseCheck(
                        data?.eventId?.extensionServiceType ?? "[]",
                        extensionType
                      )}
                    />{" "}
                    <span className="fontSet">{extensionType}</span>
                  </ul>
                );
              })}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Sustainable Development Goals: Choose the applicable SDGs to your
              extension project:
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {sdgList.map((sdg, index) => {
                return (
                  <ul key={index}>
                    {" "}
                    <PreviewCheckbox
                      checked={insensitiveCaseCheck(data?.eventId?.sdg ?? "[]", sdg)}
                    />{" "}
                    <span className="fontSet">{sdg}</span>
                  </ul>
                );
              })}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Number of Male and Female and Type of Beneficiaries (Type such as
              OSY, Children, Women, etc.):
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {data?.eventId?.beneficiaries}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Project Leader, Assistant Project Leader, Coordinators:
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {data?.eventId?.projectLeader}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Objectives:
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              {data?.eventId?.objectives}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Narrative of the Activity:
            </td>
            <td colSpan={7} className="fontSet" style={{ textAlign }}>
              <SafeHtmlRenderer htmlContent={data?.narrative || ''} />
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="fontSet">
              Evaluation Result (if activity is training, technical advice or
              seminar)
            </td>
            <td colSpan={7} className="fontSet">
              1. Number of beneficiaries/participants who rated the activity as:
              <table className="bsuFormChild" style={{ width: "95%", fontSize: "10pt" }}>
                <ColSizeGen colSize={9} percentage="11.1111%" />
                <tbody>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center", padding: "2px" }}
                      className="top fontSet"
                    ></td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    >
                      Scale
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    >
                      BatStateU Participants
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    >
                      Participants from other Institutions
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    >
                      Total
                    </td>
                  </tr>
                  <tr>
                    <td
                      colSpan={1}
                      className="fontSet"
                      style={{ textAlign: "center" }}
                    >
                      1.1
                    </td>
                    <td
                      colSpan={2}
                      className="fontSet"
                      style={{ textAlign: "center" }}
                    >
                      Excellent
                    </td>
                    <td
                      colSpan={2}
                      className="fontSet"
                      style={{ textAlign: "center" }}
                    >
                      {reportAnalytics?.insider?.evaluation?.overall
                        ?.excellent ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      className="fontSet"
                      style={{ textAlign: "center" }}
                    >
                      {reportAnalytics?.outsider?.evaluation?.overall
                        ?.excellent ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      className="fontSet"
                      style={{ textAlign: "center" }}
                    >
                      {(reportAnalytics?.outsider?.evaluation?.overall
                        ?.excellent ?? 0) +
                        (reportAnalytics?.insider?.evaluation?.overall
                          ?.excellent ?? 0)}
                    </td>
                  </tr>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      1.2
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      Very Satisfactory
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.insider?.evaluation?.overall
                        ?.verySatisfactory ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.outsider?.evaluation?.overall
                        ?.verySatisfactory ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {(reportAnalytics?.insider?.evaluation?.overall
                        ?.verySatisfactory ?? 0) +
                        (reportAnalytics?.outsider?.evaluation?.overall
                          ?.verySatisfactory ?? 0)}
                    </td>
                  </tr>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      1.3
                    </td>
                    <td
                      colSpan={2}
                      className="fontSet"
                      style={{ textAlign: "center" }}
                    >
                      Satisfactory
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.insider?.evaluation?.overall
                        ?.satisfactory ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.outsider?.evaluation?.overall
                        ?.satisfactory ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {(reportAnalytics?.insider?.evaluation?.overall
                        ?.satisfactory ?? 0) +
                        (reportAnalytics?.outsider?.evaluation?.overall
                          ?.satisfactory ?? 0)}
                    </td>
                  </tr>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      1.4
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      Fair
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.insider?.evaluation?.overall?.fair ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.outsider?.evaluation?.overall?.fair ??
                        0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {(reportAnalytics?.insider?.evaluation?.overall?.fair ??
                        0) +
                        (reportAnalytics?.outsider?.evaluation?.overall?.fair ??
                          0)}
                    </td>
                  </tr>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      1.5
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      Poor
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.insider?.evaluation?.overall?.poor ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.outsider?.evaluation?.overall?.poor ??
                        0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {(reportAnalytics?.insider?.evaluation?.overall?.poor ??
                        0) +
                        (reportAnalytics?.insider?.evaluation?.overall?.poor ??
                          0)}
                    </td>
                  </tr>
                </tbody>
              </table>
              <br />
              2. Number of beneficiaries/participants who rated the timeliness
              of the activity as:
              <table className="bsuFormChild" style={{ width: "95%" }}>
                <ColSizeGen colSize={9} percentage="11.1111%" />
                <tbody>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    ></td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    >
                      Scale
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    >
                      BatStateU Participants
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    >
                      Participants from other Institutions
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="top fontSet"
                    >
                      Total
                    </td>
                  </tr>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      2.1
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      Excellent
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.insider?.evaluation?.timeline
                        ?.excellent ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.outsider?.evaluation?.timeline
                        ?.excellent ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {(reportAnalytics?.insider?.evaluation?.timeline
                        ?.excellent ?? 0) +
                        (reportAnalytics?.outsider?.evaluation?.timeline
                          ?.excellent ?? 0)}
                    </td>
                  </tr>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      2.2
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      Very Satisfactory
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.insider?.evaluation?.timeline
                        ?.verySatisfactory ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.outsider?.evaluation?.timeline
                        ?.verySatisfactory ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {(reportAnalytics?.insider?.evaluation?.timeline
                        ?.verySatisfactory ?? 0) +
                        (reportAnalytics?.outsider?.evaluation?.timeline
                          ?.verySatisfactory ?? 0)}
                    </td>
                  </tr>
                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      2.3
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      Satisfactory
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.insider?.evaluation?.timeline
                        ?.satisfactory ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.outsider?.evaluation?.timeline
                        ?.satisfactory ?? 0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {(reportAnalytics?.outsider?.evaluation?.timeline
                        ?.satisfactory ?? 0) +
                        (reportAnalytics?.insider?.evaluation?.timeline
                          ?.satisfactory ?? 0)}
                    </td>
                  </tr>

                  <tr>
                    <td
                      colSpan={1}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      2.4
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      Fair
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.insider?.evaluation?.timeline?.fair ??
                        0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {reportAnalytics?.outsider?.evaluation?.timeline?.fair ??
                        0}
                    </td>
                    <td
                      colSpan={2}
                      style={{ textAlign: "center" }}
                      className="fontSet"
                    >
                      {(reportAnalytics?.outsider?.evaluation?.timeline?.fair ??
                        0) +
                        (reportAnalytics?.insider?.evaluation?.timeline?.fair ??
                          0)}
                    </td>
                  </tr>
                  <tr>
                    <td
                      className="fontSet"
                      colSpan={1}
                      style={{ textAlign: "center" }}
                    >
                      2.5
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      Poor
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      {reportAnalytics?.insider?.evaluation?.timeline?.poor ??
                        0}
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      {reportAnalytics?.outsider?.evaluation?.timeline?.poor ??
                        0}
                    </td>
                    <td
                      className="fontSet"
                      colSpan={2}
                      style={{ textAlign: "center" }}
                    >
                      {(reportAnalytics?.insider?.evaluation?.timeline?.poor ??
                        0) +
                        (reportAnalytics?.outsider?.evaluation?.timeline
                          ?.poor ?? 0)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
          <tr>
            <td className="fontSet" colSpan={3}>
              Photos:
            </td>
            <td className="fontSet" colSpan={7}>
              <AdminPhotoDisplay 
                photos={data?.photos || []} 
                captions={data?.photoCaptions || []}
                maxPhotos={2}
              />
            </td>
          </tr>
          <tr>
            <BSUTemplateSigning
              romaize
              colspan={5}
              upperMessage="Prepared By:"
              designation={data?.signatoriesId?.preparedTitle}
              placeHolder={data?.signatoriesId?.preparedBy}
            />
            <BSUTemplateSigning
              romaize
              colspan={5}
              upperMessage="Reviewed By:"
              designation={data?.signatoriesId?.reviewedTitle}
              placeHolder={data?.signatoriesId?.reviewedBy}
            />
          </tr>
          <tr>
            <BSUTemplateSigning
              romaize
              colspan={10}
              upperMessage="Approved By:"
              designation={data?.signatoriesId?.approvedTitle}
              placeHolder={data?.signatoriesId?.approvedBy}
            />
          </tr>
        </tbody>
      </table>
      <div className="fontSet" style={{ marginTop: "10px", fontSize: "10pt", fontFamily: "'Times New Roman', serif" }}>
        Cc: GAD Central
      </div>
    </BSUTemplateHeader>
  );
};

export default ExternalReport;
