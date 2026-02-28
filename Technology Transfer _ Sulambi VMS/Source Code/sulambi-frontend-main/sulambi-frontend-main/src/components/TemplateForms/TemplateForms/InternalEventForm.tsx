import { CheckBoxText, RomanListValues } from "./ExternalEventForm";

import { useEffect, useMemo, useState } from "react";

import { InternalEventProposalType } from "../../../interface/types";

import FlexBox from "../../FlexBox";

import BSUTemplateHeader from "./BSUTemplateHeader";

import BSUTemplateSigning from "./BSUTemplateSigning";

import ColSizeGen from "./ColSizeGen";

import dayjs from "dayjs";
import { looseJsonParse } from "../../../utils/looseJson";

interface Props {
  data: InternalEventProposalType;
}

interface InnerFormTableTemplateProps {
  textAlign?: "center" | "left" | "justify" | "right";
  customColsize?: number;
  customPercentage?: number;
  customFlexSize?: number[];
  header: string[];
  dataKeys: any[];
  data: any[];
}

export const InnerFormTableTemplate: React.FC<InnerFormTableTemplateProps> = ({
  customColsize,
  customFlexSize,
  customPercentage,
  data,
  dataKeys,
  header,
  textAlign,
}) => {
  const isMeaningfulCellValue = (value: unknown) => {
    if (value === null || value === undefined) return false;
    if (typeof value === "number") return !Number.isNaN(value);
    // Avoid treating objects as meaningful unless they are renderable strings/numbers
    if (typeof value === "object") return false;

    const raw = String(value);
    // Treat common rich-text "empty" HTML as empty
    const withoutTags = raw
      .replace(/<[^>]*>/g, "")
      .replace(/&nbsp;/g, " ")
      .replace(/\u00a0/g, " ")
      .trim();
    return withoutTags !== "";
  };

  // Remove rows that are visually empty across all configured columns.
  const filteredRows = Array.isArray(data)
    ? data.filter((rowData) => {
        if (!rowData || typeof rowData !== "object") return false;
        return dataKeys.some((colKey) => isMeaningfulCellValue((rowData as any)[colKey]));
      })
    : [];

  return (
    <div style={{ overflow: "hidden", width: "100%" }}>
      <table className="bsuFormChild internal-event-table-with-top-border" style={{ overflow: "hidden", borderTop: "1px solid black" }}>
        <ColSizeGen
          colSize={customColsize ?? header.length}
          percentage={`${customPercentage ?? 100 / header.length}%`}
        />
        <tbody>
          <tr>
            {header.map((head, id) => (
              <td
                key={id}
                colSpan={customFlexSize ? customFlexSize[id] : 1}
                style={{ textAlign, fontWeight: "normal", borderTop: "1px solid black" }}
                className="fontSet"
              >
                {head}
              </td>
            ))}
          </tr>
          {dataKeys.length === header.length ? (
            filteredRows.length === 0 ? (
              <tr>
                <td
                  colSpan={customColsize ?? header.length}
                  style={{ textAlign }}
                  className="fontSet"
                >
                  (No data)
                </td>
              </tr>
            ) : (
              filteredRows.map((rowData, rowIndex) => (
                <tr key={rowIndex}>
                  {dataKeys.map((colKeys, colId) => (
                    <td
                      key={colId}
                      colSpan={customFlexSize ? customFlexSize[colId] ?? 1 : 1}
                      style={{ textAlign }}
                      className="fontSet"
                    >
                      {rowData[colKeys]}
                    </td>
                  ))}
                </tr>
              ))
            )
          ) : (
            <></>
          )}
        </tbody>
      </table>
    </div>
  );
};

const InternalEventForm: React.FC<Props> = ({ data }) => {
  const [financialRequirement, setFinancialRequirement] = useState<any>({});
  const [evaluationMechanicsPlan, setEvaluationMechanicsPlan] = useState<any>(
    {}
  );
  const [activities, setActivities] = useState<Array<{ activity_name: string; months: number[] }>>([]);
  const [monthHeaders, setMonthHeaders] = useState<string[]>([]);

  const renderedWorkPlan = useMemo(() => {
    const parsedWorkPlan = looseJsonParse<any>(data.workPlan, {});
    if (!parsedWorkPlan || typeof parsedWorkPlan !== "object" || Array.isArray(parsedWorkPlan)) {
      return { headers: [] as string[], rows: [] as Array<{ activity: string; cells: Record<string, string> }> };
    }

    const rowKeys = Object.keys(parsedWorkPlan).sort((a, b) => (parseInt(a) || 0) - (parseInt(b) || 0));
    const headers: string[] = [];
    const headerSet = new Set<string>();

    rowKeys.forEach((k) => {
      const row = parsedWorkPlan[k];
      if (!row || typeof row !== "object") return;
      Object.keys(row).forEach((colKey) => {
        if (colKey === "Activities" || colKey === "activities") return;
        if (!headerSet.has(colKey)) {
          headerSet.add(colKey);
          headers.push(colKey);
        }
      });
    });

    const rows = rowKeys
      .map((k) => {
        const row = parsedWorkPlan[k];
        if (!row || typeof row !== "object") return null;
        const activity = String(row.Activities ?? row.activities ?? "").trim();
        if (!activity) return null;
        const cells: Record<string, string> = {};
        headers.forEach((h) => {
          const val = row[h];
          cells[h] = val === null || val === undefined ? "" : String(val);
        });
        return { activity, cells };
      })
      .filter(Boolean) as Array<{ activity: string; cells: Record<string, string> }>;

    return { headers, rows };
  }, [data.workPlan]);

  useEffect(() => {
    // Parse evaluationMechanicsPlan - handle both string and object formats
    try {
      if (data.evaluationMechanicsPlan) {
        const parsed = typeof data.evaluationMechanicsPlan === 'string' 
          ? JSON.parse(data.evaluationMechanicsPlan) 
          : data.evaluationMechanicsPlan;
        setEvaluationMechanicsPlan(parsed && typeof parsed === 'object' ? parsed : {});
      } else {
        setEvaluationMechanicsPlan({});
      }
    } catch (e) {
      console.error('Error parsing evaluationMechanicsPlan:', e);
      setEvaluationMechanicsPlan({});
    }

    // Parse financialRequirement - handle both string and object formats
    try {
      if (data.financialRequirement) {
        const parsed = typeof data.financialRequirement === 'string' 
          ? JSON.parse(data.financialRequirement) 
          : data.financialRequirement;
        setFinancialRequirement(parsed && typeof parsed === 'object' ? parsed : {});
      } else {
        setFinancialRequirement({});
      }
    } catch (e) {
      console.error('Error parsing financialRequirement:', e);
      setFinancialRequirement({});
    }

    // Prefer workPlan as source of truth. activities can be stale/backfilled data.
    if (data.workPlan) {
      // Convert workPlan format to activities format
      try {
        const parsedWorkPlan = looseJsonParse<any>(data.workPlan, {});
        const convertedActivities: Array<{ activity_name: string; months: number[] }> = [];
        
        // Extract column headers from row keys in the data
        let allMonthHeaders: string[] = [];
        const headerSet = new Set<string>();
        const firstRowKey = Object.keys(parsedWorkPlan || {})[0];
        
        if (firstRowKey && parsedWorkPlan[firstRowKey]) {
          // Preserve order from first row
          Object.keys(parsedWorkPlan[firstRowKey]).forEach((colKey) => {
            if (colKey !== 'Activities' && colKey !== 'activities' && !headerSet.has(colKey)) {
              headerSet.add(colKey);
              allMonthHeaders.push(colKey);
            }
          });
          // Add columns that appear only in other rows
          Object.keys(parsedWorkPlan).forEach((key) => {
            const row = parsedWorkPlan[key];
            if (row) {
              Object.keys(row).forEach((colKey) => {
                if (colKey !== 'Activities' && colKey !== 'activities' && !headerSet.has(colKey)) {
                  headerSet.add(colKey);
                  allMonthHeaders.push(colKey);
                }
              });
            }
          });
        } else {
          Object.keys(parsedWorkPlan || {}).forEach((key) => {
            const row = parsedWorkPlan[key];
            if (row) {
              Object.keys(row).forEach((colKey) => {
                if (colKey !== 'Activities' && colKey !== 'activities' && !headerSet.has(colKey)) {
                  headerSet.add(colKey);
                  allMonthHeaders.push(colKey);
                }
              });
            }
          });
        }
        
        const allAreDefaultFormat = allMonthHeaders.every(h => 
          /^Month \d+$/.test(h) || /^act_\d+$/.test(h)
        );
        if (allAreDefaultFormat) {
          allMonthHeaders.sort((a, b) => {
            const numA = parseInt(a.replace(/Month |act_/g, '')) || 0;
            const numB = parseInt(b.replace(/Month |act_/g, '')) || 0;
            if (numA > 0 && numB > 0) {
              return numA - numB;
            }
            return 0;
          });
        }
        
        setMonthHeaders(allMonthHeaders);
        
        Object.keys(parsedWorkPlan || {}).forEach((key) => {
          const row = parsedWorkPlan[key];
          if (!row) return;

          const activityName = row.Activities || row.activities;
          if (!activityName || activityName.trim() === '') return;

          const months: number[] = [];
          allMonthHeaders.forEach((monthHeader, index) => {
            const monthValue = row[monthHeader];
            const normalized = typeof monthValue === 'string' ? monthValue.trim() : monthValue;
            if (normalized === '' || normalized === null || normalized === undefined) return;
            // Guard against corrupted rows where month cells mirror the activity name.
            if (typeof normalized === 'string' && normalized.toLowerCase() === String(activityName).trim().toLowerCase()) return;
            months.push(index);
          });

          if (months.length > 0) {
            convertedActivities.push({
              activity_name: activityName,
              months
            });
          }
        });
        
        if (convertedActivities.length > 0) {
          setActivities(convertedActivities);
        } else if (data.activities && Array.isArray(data.activities) && data.activities.length > 0) {
          // Fallback to API activities only when workPlan has no usable rows.
          setActivities(data.activities);
        } else {
          setActivities([]);
        }
      } catch (e) {
        console.error('Error parsing workPlan:', e);
        if (data.activities && Array.isArray(data.activities) && data.activities.length > 0) {
          setActivities(data.activities);
        } else {
          setActivities([]);
          setMonthHeaders([]);
        }
      }
    } else if (data.activities && Array.isArray(data.activities) && data.activities.length > 0) {
      // If activities exist and have data, use them and extract monthHeaders from them
      setActivities(data.activities);
      // Extract unique month headers from activities (if months are indices, we need to know the headers)
      // Since activities from API don't have month headers, we need to check workPlan for headers
      if (data.workPlan) {
        try {
          const parsedWorkPlan = looseJsonParse<any>(data.workPlan, {});
          if (parsedWorkPlan && typeof parsedWorkPlan === 'object' && Object.keys(parsedWorkPlan).length > 0) {
            // Extract month headers from workPlan to display column headers
            const headerSet = new Set<string>();
            const allMonthHeaders: string[] = [];
            
            // Extract from first row
            const firstRowKey = Object.keys(parsedWorkPlan)[0];
            if (firstRowKey && parsedWorkPlan[firstRowKey]) {
              Object.keys(parsedWorkPlan[firstRowKey]).forEach((colKey) => {
                if (colKey !== 'Activities' && colKey !== 'activities' && !headerSet.has(colKey)) {
                  headerSet.add(colKey);
                  allMonthHeaders.push(colKey);
                }
              });
            }
            
            // Check all rows for any additional headers
            Object.keys(parsedWorkPlan).forEach((key) => {
              const row = parsedWorkPlan[key];
              if (row) {
                Object.keys(row).forEach((colKey) => {
                  if (colKey !== 'Activities' && colKey !== 'activities' && !headerSet.has(colKey)) {
                    headerSet.add(colKey);
                    allMonthHeaders.push(colKey);
                  }
                });
              }
            });
            
            if (allMonthHeaders.length > 0) {
              // Sort only if all are default format
              const allAreDefaultFormat = allMonthHeaders.every(h => 
                /^Month \d+$/.test(h) || /^act_\d+$/.test(h)
              );
              if (allAreDefaultFormat) {
                allMonthHeaders.sort((a, b) => {
                  const numA = parseInt(a.replace(/Month |act_/g, '')) || 0;
                  const numB = parseInt(b.replace(/Month |act_/g, '')) || 0;
                  if (numA > 0 && numB > 0) {
                    return numA - numB;
                  }
                  return 0;
                });
              }
              setMonthHeaders(allMonthHeaders);
            }
          }
        } catch (e) {
          console.error('Error extracting month headers from workPlan:', e);
        }
      }
    } else {
      // If neither activities nor workPlan exist, reset to empty state
      setActivities([]);
      setMonthHeaders([]);
    }
  }, [data]);


  return (
    <BSUTemplateHeader
      formTitle="GAD PROPOSAL (INTERNAL PROGRAM/PROJECT/ACTIVITY)"
      reference="Reference No.: BatStateU-FO-ESO-09"
      effectivityDate="Effectivity Date: August 25, 2023"
      revisionNumber="Revision No.: 00"
      romaize
    >
      <table className="bsuFormChild internal-event-table-with-top-border" style={{ marginTop: 0, borderTop: "1px solid black", borderSpacing: 0, pageBreakBefore: "auto", breakBefore: "auto" }}>
        <ColSizeGen colSize={2} percentage="50%" />
        <tbody>
          <tr>
            <td colSpan={2} className="fontSet">
              <FlexBox justifyContent="space-around">
                <CheckBoxText
                  romaize
                  message="Program"
                  checked={data.eventProposalType?.includes("Program") ?? false}
                />
                <CheckBoxText
                  romaize
                  message="Project"
                  checked={data.eventProposalType?.includes("Project") ?? false}
                />
                <CheckBoxText
                  romaize
                  message="Activity"
                  checked={
                    data.eventProposalType?.includes("Activity") ?? false
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
                  { title: "Title: ", value: data.title },
                    {
                      title: "Date and Venue: ",
                    value: `${data.venue} (${dayjs(data.durationStart).format(
                      "MMMM D, YYYY h:mm A"
                    )} - ${dayjs(data.durationEnd).format(
                      "MMMM D, YYYY h:mm A"
                    )})`,
                    },
                    {
                      title: "Mode of delivery (online/face-to-face): ",
                    value: data.modeOfDelivery,
                    },
                    {
                      title: "Project Team: ",
                    value: data.projectTeam,
                      newlineAfterValue: true,
                    },
                    {
                      title: "Partner Office/College/Department: ",
                    value: data.partner,
                    },
                    {
                      title: "Type of Participants: ",
                      value: (
                        <>
                          <div>{data.participant}</div>

                          {/* --- Type of Participants Table (small + centered like your sample) --- */}
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "center",
                              alignItems: "center",
                              width: "30%",
                              marginTop: "4px",
                              marginBottom: "6px",
                              marginLeft: "auto",
                              marginRight: "auto",
                            }}
                          >
                            <table
                              className="participant-table bsuFormChild internal-event-table-with-top-border"
                              style={{
                                width: "100%",
                                fontSize: "8.5pt",
                                borderCollapse: "collapse",
                                tableLayout: "fixed",
                                background: "#fff",
                                borderTop: "1px solid black",
                              }}
                            >
                              <colgroup>
                                <col style={{ width: "35%" }} />
                                <col style={{ width: "35%" }} />
                              </colgroup>

                              <tbody>
                                {/* top header row */}
                                <tr>
                                  <td
                                    style={{
                                      padding: "2px 4px",
                                      borderTop: "1px solid #000",
                                      borderLeft: "1px solid #000",
                                      borderBottom: "1px solid #000",
                                      borderRight: "none",
                                      textAlign: "center",
                                    }}
                                  ></td>
                                  <td
                                    style={{
                                      padding: "2px 4px",
                                      border: "1px solid #000",
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
                                      borderLeft: "1px solid #000",
                                      borderBottom: "1px solid #000",
                                      textAlign: "center",
                                    }}
                                  >
                                    Male
                                  </td>
                                  <td
                                    style={{
                                      padding: "2px 4px",
                                      borderRight: "1px solid #000",
                                      borderBottom: "1px solid #000",
                                      textAlign: "center",
                                    }}
                                  >
                                    {data.maleTotal ?? ""}
                                  </td>
                                </tr>

                                {/* female row */}
                                <tr>
                                  <td
                                    style={{
                                      padding: "2px 4px",
                                      borderLeft: "1px solid #000",
                                      borderBottom: "1px solid #000",
                                      textAlign: "center",
                                    }}
                                  >
                                    Female
                                  </td>
                                  <td
                                    style={{
                                      padding: "2px 4px",
                                      borderRight: "1px solid #000",
                                      borderBottom: "1px solid #000",
                                      textAlign: "center",
                                    }}
                                  >
                                    {data.femaleTotal ?? ""}
                                  </td>
                                </tr>

                                {/* total row */}
                                <tr>
                                  <td
                                    style={{
                                      padding: "2px 4px",
                                      borderLeft: "1px solid #000",
                                      borderBottom: "1px solid #000",
                                      fontWeight: 600,
                                      textAlign: "center",
                                    }}
                                  >
                                    Total
                                  </td>
                                  <td
                                    style={{
                                      padding: "2px 4px",
                                      borderRight: "1px solid #000",
                                      borderBottom: "1px solid #000",
                                      textAlign: "center",
                                      fontWeight: 600,
                                    }}
                                  >
                                    {(Number(data.maleTotal) || 0) + (Number(data.femaleTotal) || 0)}
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        </>
                      ),
                    },
                    {
                      title: "Rationale/Background: ",
                    value: data.rationale,
                      newlineAfterValue: true,
                    },
                    {
                      title: "Objectives: ",
                    value: data.objectives,
                      newlineAfterValue: true,
                    },
                    {
                      title:
                        "Description, Strategies and Methods (Activities / Schedule): ",
                    value: data.description,
                      newlineAfterValue: true,
                    },
                  {
                    title: "Work Plan (Timeline of Activities/Gantt Chart): ",
                  },
                  ]}
                />
              <div style={{ width: "90%", margin: "0 auto" }}>
                {((renderedWorkPlan.rows.length > 0 && renderedWorkPlan.headers.length > 0) || (activities.length > 0 && monthHeaders.length > 0)) ? (
                  <div className="workplan-table-wrapper" style={{ overflow: "hidden", width: "100%" }}>
                    <table className="bsuFormChild workplan-table internal-event-table-with-top-border" style={{ overflow: "hidden", width: "100%", borderTop: "1px solid black" }}>
                      <ColSizeGen colSize={(renderedWorkPlan.headers.length || monthHeaders.length) + 1} percentage={`${100 / ((renderedWorkPlan.headers.length || monthHeaders.length) + 1)}%`} />
                      <tbody>
                        <tr>
                          <td colSpan={1} style={{ textAlign: "center", fontWeight: "normal", borderTop: "1px solid black", padding: "4px 6px", fontSize: "11px" }} className="fontSet">
                            Activities
                          </td>
                          {(renderedWorkPlan.headers.length > 0 ? renderedWorkPlan.headers : monthHeaders).map((header, headerIndex) => {
                            // Display EXACTLY what the officer entered - no processing, no stripping
                            // If they put "Nov 14 2025", show "Nov 14 2025"
                            // If they put "Month 1", show "Month 1"
                            // If they put "★", show "★"
                            // Display the header exactly as it appears in the data
                            return (
                              <td
                                key={headerIndex}
                                colSpan={1}
                                style={{ textAlign: "center", fontWeight: "normal", borderTop: "1px solid black", padding: "4px 6px", fontSize: "11px" }}
                                className="fontSet"
                              >
                                {header}
                              </td>
                            );
                          })}
                        </tr>
                        {(renderedWorkPlan.rows.length > 0
                          ? renderedWorkPlan.rows.map((row) => ({
                              activity_name: row.activity,
                              cells: row.cells,
                              months: [] as number[],
                            }))
                          : activities.map((activity) => ({
                              activity_name: activity.activity_name,
                              cells: {} as Record<string, string>,
                              months: activity.months,
                            }))
                        ).map((activity, rowIndex) => (
                          <tr key={rowIndex}>
                            <td
                              colSpan={1}
                              style={{ textAlign: "left", padding: "4px 6px", fontSize: "11px" }}
                              className="fontSet"
                            >
                              {activity.activity_name}
                            </td>
                            {(renderedWorkPlan.headers.length > 0 ? renderedWorkPlan.headers : monthHeaders).map((header, headerIndex) => (
                              <td
                                key={headerIndex}
                                colSpan={1}
                                style={{ textAlign: "center", padding: "4px 6px", fontSize: "11px" }}
                                className="fontSet"
                              >
                                {renderedWorkPlan.rows.length > 0
                                  ? (activity.cells[header] || "")
                                  : (activity.months.includes(headerIndex) ? "X" : "")}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{ overflow: "hidden", width: "100%" }}>
                    <table className="bsuFormChild internal-event-table-with-top-border" style={{ overflow: "hidden", width: "100%", borderTop: "1px solid black" }}>
                      <ColSizeGen colSize={1} percentage="100%" />
                      <tbody>
                        <tr>
                          <td className="fontSet" style={{ textAlign: "center", borderTop: "1px solid black" }}>
                            (No data)
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* XI. Financial Requirements stays on page 1 */}
              <RomanListValues
                romaize
                marginBetween="10px"
                start={11}
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

              {/* Page 2 starts here */}
              <div className="internal-event-page-break" />

              <RomanListValues
                romaize
                marginBetween="10px"
                start={12}
                list={[
                  {
                    title: "Monitoring and Evaluation Mechanics / Plan: ",
                  },
                ]}
              />
                <div style={{ width: "90%", margin: "0 auto" }}>
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
                <RomanListValues
                romaize
                marginBetween="10px"
                  start={13}
                  list={[
                    {
                      title: "Sustainability Plan: ",
                    value: data.sustainabilityPlan,
                    },
                  ]}
                />
            </td>
          </tr>
          <tr>
            <BSUTemplateSigning
              colspan={1}
              upperMessage={
                data?.signatoriesId?.preparedTitle !== "" &&
                data?.signatoriesId?.preparedBy !== ""
                  ? "Prepared By:"
                  : ""
              }
              designation={data?.signatoriesId?.preparedTitle}
              placeHolder={data?.signatoriesId?.preparedBy}
              romaize
            />
            <BSUTemplateSigning
              colspan={1}
              upperMessage={
                data?.signatoriesId?.reviewedTitle !== "" &&
                data?.signatoriesId?.reviewedBy
                  ? "Reviewed By:"
                  : ""
              }
              designation={data?.signatoriesId?.reviewedTitle}
              placeHolder={data?.signatoriesId?.reviewedBy}
              romaize
            />
          </tr>
          <tr>
            <BSUTemplateSigning
              colspan={1}
              upperMessage={
                data?.signatoriesId?.recommendingSignatory1 !== "" &&
                data?.signatoriesId?.recommendingApproval1 !== ""
                  ? "Recommending approval:"
                  : ""
              }
              designation={data?.signatoriesId?.recommendingSignatory1}
              placeHolder={data?.signatoriesId?.recommendingApproval1}
              romaize
            />
            <BSUTemplateSigning
              colspan={1}
              upperMessage={
                data?.signatoriesId?.recommendingSignatory2 !== "" &&
                data?.signatoriesId?.recommendingApproval2 !== ""
                  ? "Recommending approval:"
                  : ""
              }
              designation={data?.signatoriesId?.recommendingSignatory2}
              placeHolder={data?.signatoriesId?.recommendingApproval2}
              romaize
            />
          </tr>
          <tr>
            <BSUTemplateSigning
              colspan={2}
              upperMessage={
                data?.signatoriesId?.approvedTitle !== "" &&
                data?.signatoriesId?.approvedBy
                  ? "Approved By:"
                  : ""
              }
              designation={data?.signatoriesId?.approvedTitle}
              placeHolder={data?.signatoriesId?.approvedBy}
              romaize
            />
          </tr>
        </tbody>
      </table>
      <div
        className="fontSet"
        style={{
          marginTop: "10px",
          fontSize: "10pt",
          fontFamily: "'Times New Roman', serif",
          fontStyle: "italic",
        }}
      >
        Cc: GAD Central
      </div>
    </BSUTemplateHeader>
  );
};

export default InternalEventForm;
