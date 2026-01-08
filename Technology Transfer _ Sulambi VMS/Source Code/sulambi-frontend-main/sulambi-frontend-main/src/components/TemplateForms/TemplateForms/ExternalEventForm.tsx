import FlexBox from "../../FlexBox";
import BSUTemplateHeader from "./BSUTemplateHeader";
import ColSizeGen from "./ColSizeGen";
import BSUTemplateSigning from "./BSUTemplateSigning";
import SafeHtmlRenderer from "../../Inputs/SafeHtmlRenderer";

import { stripLeadingRoman } from "../../../utils/stripLeadingRoman";

// import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
// import CheckBoxIcon from "@mui/icons-material/CheckBox";
import { ExternalEventProposalType } from "../../../interface/types";
import dayjs from "dayjs";
interface CheckBoxTextProps {
  checked?: boolean;
  message?: string;
  romaize?: boolean;
}

interface EvaluationMechanicsProps {
  data: any;
}

interface RomanListValuesProps {
  marginBetween?: string;
  start?: number;
  romaize?: boolean;
  list: {
    title: string;
    multipleValue?: boolean;
    newlineAfterValue?: boolean;
    value?: any;
    disableList?: boolean;
  }[];
}

interface FormProps {
  data: ExternalEventProposalType;
}

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

type FinancialPlanRow = {
  item?: string;
  qty?: string | number;
  unit?: string;
  unitCost?: string | number;
  total?: string | number;
};

const formatCurrency = (
  amount: number,
  locale: string = "en-PH",
  currency: string = "PHP"
) => {
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(
    amount
  );
};

export const PreviewCheckbox: React.FC<{ checked?: boolean }> = ({ checked }) => (
  <span
    className={`preview-checkbox${checked ? " preview-checkbox--checked" : ""}`}
    role="checkbox"
    aria-checked={checked ? "true" : "false"}
  />
);

export const CheckBoxText: React.FC<CheckBoxTextProps> = ({
  checked,
  message,
  romaize,
}) => {
  return (
    <FlexBox
      alignItems="center"
      gap="5px"
      className={romaize ? "fontSet" : undefined}
    >
      <PreviewCheckbox checked={checked} />
      {message}
    </FlexBox>
  );
};

const normalizeFinancialPlan = (raw: any): FinancialPlanRow[] => {
  if (!raw) return [];
  let parsed: any = raw;
  try {
    if (typeof raw === "string") {
      parsed = raw.trim() === "" ? {} : JSON.parse(raw);
    }
  } catch {
    // legacy plain text -> single row with item only
    return [{ item: String(raw).trim() }];
  }

  // If already array of rows
  if (Array.isArray(parsed)) {
    return parsed as FinancialPlanRow[];
  }

  // If keyed object from field repeater: { 0: {...}, 1: {...} }
  if (parsed && typeof parsed === "object") {
    const keys = Object.keys(parsed).sort((a, b) => Number(a) - Number(b));
    return keys.map(k => parsed[k]) as FinancialPlanRow[];
  }

  // Fallback: single item string
  return [{ item: String(parsed) }];
};

const FinancialPlanTable: React.FC<{ value: any }> = ({ value }) => {
  const rows = normalizeFinancialPlan(value);

  const formatText = (s: any) =>
    String(s ?? "")
      .replace(/<[^>]+>/g, "") // strip HTML tags so preview shows plain text
      .trim();

  const ensure = (row: FinancialPlanRow): Required<FinancialPlanRow> => ({
    item: row.item ?? "",
    qty: row.qty ?? "",
    unit: row.unit ?? "",
    unitCost: row.unitCost ?? "",
    total: row.total ?? "",
  });

  return (
    <table
      className="bsuFormChild financial-plan internal-event-table-with-top-border"
      style={{
        width: "300px",     // smaller fixed width
        maxWidth: "100%",   // allow expansion if content is too wide
        minWidth: "300px",  // maintain minimum size
        margin: "0 auto",
        tableLayout: "auto", // allow columns to adjust based on content
        borderCollapse: "collapse",
        border: "0.5px solid #666", // Lighter, thinner border
        borderTop: "0.5px solid #666", // Lighter, thinner border
        fontSize: "10pt",
      }}
    >
      <colgroup>
        <col width="150px" />
        <col width="36px" />
        <col width="36px" />
        <col width="39px" />
        <col width="39px" />
      </colgroup>
      <thead>
        <tr>
          <th className="fontSet" style={{ fontWeight: "bold", textAlign: "center", padding: "2px 3px", border: "0.5px solid #666" }}>Item Description</th>
          <th className="fontSet" style={{ fontWeight: "bold", textAlign: "center", padding: "2px 3px", border: "0.5px solid #666" }}>Quantity</th>
          <th className="fontSet" style={{ fontWeight: "bold", textAlign: "center", padding: "2px 3px", border: "0.5px solid #666" }}>Unit</th>
          <th className="fontSet" style={{ fontWeight: "bold", textAlign: "center", padding: "2px 3px", border: "0.5px solid #666" }}>Unit Cost</th>
          <th className="fontSet" style={{ fontWeight: "bold", textAlign: "center", padding: "2px 3px", border: "0.5px solid #666" }}>Total</th>
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 && (
          <tr>
            <td className="fontSet" colSpan={5} style={{ textAlign: "center", padding: "10px 8px" }}>
              (No data)
            </td>
          </tr>
        )}
        {rows.map((r, idx) => {
          const row = ensure(r);
          return (
            <tr key={idx}>
              <td
                className="fontSet"
                style={{
                  wordWrap: "break-word",
                  overflowWrap: "break-word",
                  wordBreak: "break-word",
                  whiteSpace: "normal",
                  verticalAlign: "top",
                  padding: "2px 3px",
                  textAlign: "center",
                  border: "0.5px solid #000", // Ultra thin black border
                }}
              >
                {formatText(row.item)}
              </td>
              <td className="fontSet" style={{ textAlign: "center", verticalAlign: "top", wordWrap: 'break-word', overflowWrap: 'break-word', wordBreak: 'break-word', whiteSpace: 'normal', padding: "2px 2px", border: "0.5px solid #666" }}>
                {formatText(row.qty)}
              </td>
              <td className="fontSet" style={{ textAlign: "center", verticalAlign: "top", wordWrap: 'break-word', overflowWrap: 'break-word', wordBreak: 'break-word', whiteSpace: 'normal', padding: "2px 2px", border: "0.5px solid #666" }}>
                {formatText(row.unit)}
              </td>
              <td className="fontSet" style={{ textAlign: "center", verticalAlign: "top", wordWrap: 'break-word', overflowWrap: 'break-word', wordBreak: 'break-word', whiteSpace: 'normal', padding: "2px 2px", border: "0.5px solid #666" }}>
                {formatText(row.unitCost)}
              </td>
              <td className="fontSet" style={{ textAlign: "center", verticalAlign: "top", wordWrap: 'break-word', overflowWrap: 'break-word', wordBreak: 'break-word', whiteSpace: 'normal', padding: "2px 2px", border: "0.5px solid #666" }}>
                {formatText(row.total)}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export const RomanListValues: React.FC<RomanListValuesProps> = ({
  list,
  start,
  marginBetween,
  romaize,
}) => {
  // Helper function to convert number to Roman numeral
  const toRoman = (num: number): string => {
    const romanNumerals: { [key: number]: string } = {
      1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X',
      11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV', 16: 'XVI', 17: 'XVII', 18: 'XVIII', 19: 'XIX', 20: 'XX',
      21: 'XXI', 22: 'XXII', 23: 'XXIII', 24: 'XXIV', 25: 'XXV', 26: 'XXVI', 27: 'XXVII', 28: 'XXVIII', 29: 'XXIX', 30: 'XXX'
    };
    return romanNumerals[num] || num.toString();
  };
  // Helper function to check if a value contains HTML
  const isHtmlContent = (value: any): boolean => {
    if (!value || typeof value !== 'string') return false;
    return /<[^>]+>/g.test(value);
  };

  // Helper function to render value (with HTML support)
  const renderValue = (value: any, isNewline: boolean) => {
    if (!value && value !== 0) return null;
    
    // If it's HTML content, use SafeHtmlRenderer
    if (typeof value === 'string' && isHtmlContent(value)) {
      return <SafeHtmlRenderer htmlContent={value} />;
    }
    
    // Otherwise render normally
    if (isNewline) {
      if (typeof value === 'string' || value instanceof String) {
        return (
          <ul
            className={romaize ? "fontSet" : undefined}
            style={{
              marginTop: "5px",
              listStyleType: "none",
              paddingLeft: 0,
              fontFamily: "'Times New Roman', serif",
              fontSize: "10pt",
            }}
          >
            {value.toString().split("\n").map((data, idx) => (
              <li key={idx}>{data}</li>
            ))}
          </ul>
        );
      } else if (Array.isArray(value)) {
        return (
          <ul
            className={romaize ? "fontSet" : undefined}
            style={{
              marginTop: "5px",
              listStyleType: "none",
              paddingLeft: 0,
              fontFamily: "'Times New Roman', serif",
              fontSize: "10pt",
            }}
          >
            {value.map((data, idx) => <li key={idx}>{data}</li>)}
          </ul>
        );
      }
    }
    
    return value;
  };

  const currentStart = start ?? 1;
  
  // IMPORTANT: use a div (not <ol>) so we don't get any automatic browser-generated numbering.
  return (
    <div
      className={romaize ? "fontSet" : undefined}
      style={{
        marginLeft: "50px", // Increased from 40px to move content slightly to the right
        marginRight: "10px",
        paddingLeft: 0,
        paddingRight: 0,
        fontFamily: "'Times New Roman', serif",
        fontSize: "10pt",
      }}
    >
      {list.map((values, index) => {
        const itemNumber = currentStart + index;
        return (
          <div
            key={index}
            className={`${romaize ? "fontSet" : ""} roman-list-item`}
            style={{
              margin: `${marginBetween ?? "8px"} 0px`,
              marginTop: "10px",
              marginBottom: "10px",
              lineHeight: "1.5",
              position: "relative",
              paddingLeft: "2.3em", // space for the manual roman label (slightly reduced from 2.5em)
              fontFamily: "'Times New Roman', serif",
              fontSize: "10pt",
            }}
          >
            {/* manual roman numeral label (no browser numbering) */}
            <span
              aria-hidden="true"
              style={{
                position: "absolute",
                left: "0", // keep at 0 to avoid clipping, but reduce width
                top: 0,
                fontWeight: "normal",
                display: "inline-block",
                width: "2.3em", // reduced from 3.6em to give more space for content
                fontFamily: "'Times New Roman', serif",
                fontSize: "10pt",
              }}
            >
              {toRoman(itemNumber)}.
            </span>

            {/* content */}
            <div
              style={{
                marginLeft: "0.1em", // reduced from 0.2em
                paddingRight: "8px", // Reduced padding to move content slightly to the right
                fontFamily: "'Times New Roman', serif",
                fontSize: "10pt",
              }}
            >
              <b
                className={romaize ? "fontSet" : undefined}
                style={{
                  fontWeight: "bold",
                  display: "inline",
                  fontFamily: "'Times New Roman', serif",
                  fontSize: "10pt",
                }}
              >
                {values.title}
              </b>

              {!values.newlineAfterValue && (
                <div style={{ display: "inline", textAlign: "justify", marginLeft: "0.4em" }}>
                  {renderValue(values.value, false)}
                </div>
              )}

              {values.newlineAfterValue && !values.multipleValue && (
                <div
                  style={{
                    marginTop: "5px",
                    textIndent: "0",
                    textAlign: "justify",
                    marginLeft: "0",
                    fontFamily: "'Times New Roman', serif",
                    fontSize: "10pt",
                  }}
                >
                  {renderValue(values.value, true)}
                </div>
              )}

              {values.newlineAfterValue && values.multipleValue && (
                <ul
                  className={romaize ? "fontSet" : undefined}
                  style={{
                    marginTop: "5px",
                    marginLeft: "0",
                    listStyleType: values.disableList ? "none" : undefined,
                    paddingLeft: values.disableList ? 0 : undefined,
                    fontFamily: "'Times New Roman', serif",
                    fontSize: "10pt",
                  }}
                >
                  {typeof values.value === "string" || values.value instanceof String
                    ? values.value.toString().split("\n").map((data, idx) => <li key={idx} style={{ marginBottom: "3px" }}>{data}</li>)
                    : Array.isArray(values.value)
                    ? values.value.map((data, idx) => (
                        <li key={idx} style={{ marginBottom: "3px", display: "block" }}>{data}</li>
                      ))
                    : renderValue(values.value, false)}
                </ul>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

const EvaluationMechanicsTable: React.FC<EvaluationMechanicsProps> = ({
  data,
}) => {
  // Helper function to get objective label
  // Note: data is already the parsed evaluationMechanicsPlan object (not the full event data)
  const getObjectiveLabel = (labelKey: string, defaultValue: string): string => {
    if (!data || typeof data !== 'object') return defaultValue;
    
    // data is already the parsed evaluationMechanicsPlan object
    return data[labelKey] || defaultValue;
  };
  return (
    <table className="bsuFormChild compact eval-compact internal-event-table-with-top-border" style={{ border: "0.5px solid #000", borderTop: "0.5px solid #000", borderBottom: "0.5px solid #000", borderLeft: "0.5px solid #000", borderRight: "0.5px solid #000", outline: "none", marginLeft: "auto", marginRight: "auto", width: "90%", boxSizing: "border-box", borderCollapse: "collapse", borderSpacing: 0, fontSize: "10pt", tableLayout: "fixed", maxWidth: "90%" }}>
      <colgroup>
        <col style={{ width: "5%" }} /> {/* Objectives - reduced */}
        <col style={{ width: "8%" }} /> {/* Performance Indicator - made smaller */}
        <col style={{ width: "7%" }} /> {/* Baseline Data - reduced */}
        <col style={{ width: "7%" }} /> {/* Performance Target - reduced */}
        <col style={{ width: "7%" }} /> {/* Data Source - reduced */}
        <col style={{ width: "9%" }} /> {/* Collection Method - reduced */}
        <col style={{ width: "8%" }} /> {/* Frequency of Data Collection - made smaller */}
        <col style={{ width: "8%" }} /> {/* Offices/Persons Responsible - made smaller */}
      </colgroup>
      <tbody>
        <tr>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            fontWeight: "bold",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            Objectives
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "middle",
            fontWeight: "bold",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            Performance Indicator
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "middle",
            fontWeight: "bold",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            Baseline Data
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "middle",
            fontWeight: "bold",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            Performance Target
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "middle",
            fontWeight: "bold",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            Data Source
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "middle",
            fontWeight: "bold",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            Collection Method
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "middle",
            fontWeight: "bold",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            Frequency of Data Collection
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "middle",
            fontWeight: "bold",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            Offices/ Persons Responsible
          </td>
        </tr>
        <tr>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {getObjectiveLabel("objectivesImpactLabel", "Impact")}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesImpact
              ? data.objectivesImpact.performanceIndicator ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesImpact
              ? data.objectivesImpact.baselineData ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesImpact
              ? data.objectivesImpact.performanceTarget ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesImpact
              ? data.objectivesImpact.dataSource ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesImpact
              ? data.objectivesImpact.collectionMethod ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesImpact
              ? data.objectivesImpact.frequencyOfDataCollection ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesImpact
              ? data.objectivesImpact.officeResponsible ?? ""
              : ""}
          </td>
        </tr>
        <tr>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {getObjectiveLabel("objectivesOutcomeLabel", "Outcome")}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutcome
              ? data.objectivesOutcome.performanceIndicator ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutcome
              ? data.objectivesOutcome.baselineData ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutcome
              ? data.objectivesOutcome.performanceTarget ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutcome
              ? data.objectivesOutcome.dataSource ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutcome
              ? data.objectivesOutcome.collectionMethod ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutcome
              ? data.objectivesOutcome.frequencyOfDataCollection ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutcome
              ? data.objectivesOutcome.officeResponsible ?? ""
              : ""}
          </td>
        </tr>
        <tr>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {getObjectiveLabel("objectivesOutputLabel", "Output")}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutput
              ? data.objectivesOutput.performanceIndicator ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutput
              ? data.objectivesOutput.baselineData ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutput
              ? data.objectivesOutput.performanceTarget ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutput
              ? data.objectivesOutput.dataSource ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutput
              ? data.objectivesOutput.collectionMethod ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutput
              ? data.objectivesOutput.frequencyOfDataCollection ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesOutput
              ? data.objectivesOutput.officeResponsible ?? ""
              : ""}
          </td>
        </tr>
        <tr>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {getObjectiveLabel("objectivesActivitiesLabel", "Activities")}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesActivities
              ? data.objectivesActivities.performanceIndicator ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesActivities
              ? data.objectivesActivities.baselineData ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesActivities
              ? data.objectivesActivities.performanceTarget ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesActivities
              ? data.objectivesActivities.dataSource ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesActivities
              ? data.objectivesActivities.collectionMethod ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesActivities
              ? data.objectivesActivities.frequencyOfDataCollection ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesActivities
              ? data.objectivesActivities.officeResponsible ?? ""
              : ""}
          </td>
        </tr>
        <tr>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {getObjectiveLabel("objectivesInputLabel", "Input")}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesInput
              ? data.objectivesInput.performanceIndicator ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesInput
              ? data.objectivesInput.baselineData ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesInput
              ? data.objectivesInput.performanceTarget ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesInput ? data.objectivesInput.dataSource ?? "" : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesInput
              ? data.objectivesInput.collectionMethod ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesInput
              ? data.objectivesInput.frequencyOfDataCollection ?? ""
              : ""}
          </td>
          <td className="fontSet" colSpan={1} style={{ 
            wordWrap: "break-word",
            overflowWrap: "break-word",
            wordBreak: "break-word",
            whiteSpace: "normal",
            verticalAlign: "top",
            textAlign: "center",
            padding: "1px 2px",
            border: "0.5px solid #000", // Ultra thin black border
            minWidth: "0",
            overflow: "hidden"
          }}>
            {data.objectivesInput
              ? data.objectivesInput.officeResponsible ?? ""
              : ""}
          </td>
        </tr>
      </tbody>
    </table>
  );
};

const ExternalEventForm: React.FC<FormProps> = ({ data }) => {
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

  return (
    <BSUTemplateHeader
      formTitle="EXTENSION PROGRAM PLAN / PROPOSAL"
      reference="Reference No.: BatStateU-FO-ESO-01"
      effectivityDate="Effectivity Date: August 25, 2023"
      revisionNumber="Revision No.: 03"
      romaize
    >
      {/*
        Build the main roman list dynamically so that when items are added/removed
        the subsequent sections (with start=...) automatically adjust numbering.
      */}
      {(() => {
        const mainList = [
          { title: "Title: ", value: stripLeadingRoman(data.title) },
          {
            title: "Location: ",
            value: stripLeadingRoman(data.location),
          },
          {
            title: "Duration: ",
            value: stripLeadingRoman(
              `${dayjs(data.durationStart).format("MMMM D, YYYY h:mm A")} - ${dayjs(data.durationEnd).format("MMMM D, YYYY h:mm A")}`
            ),
          },
          {
            title: "Type of Extension Service Agenda: ",
            value: extensionServiceList.map((extensionType, idx) => (
              <span key={extensionType + idx} className="fontSet" style={{ display: "block", marginBottom: "2px" }}>
                <PreviewCheckbox
                  checked={insensitiveCaseCheck(
                    data.extensionServiceType,
                    extensionType
                  )}
                />
                {extensionType}
              </span>
            )),
            disableList: true,
            multipleValue: true,
            newlineAfterValue: true,
          },
          {
            title: "Sustainable Development Goal :",
            newlineAfterValue: true,
            multipleValue: true,
            disableList: true,
            value: sdgList.map((sdg, idx) => (
              <span key={sdg + idx} className="fontSet" style={{ display: "block", marginBottom: "2px" }}>
                <PreviewCheckbox
                  checked={insensitiveCaseCheck(data.sdg, sdg)}
                />
                {sdg}
              </span>
            )),
          },
          {
            title:
              "Office(s) / College(s) / Organization(s) Involved :",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.orgInvolved),
          },
          {
            title:
              "Program/s Involved (specify the programs under the college :",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.programInvolved),
          },
          {
            title:
              "Project Leader, Assistant Project Leader and Coordinators :",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.projectLeader),
          },
          {
            title: "Partner Agencies: ",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.partners),
          },
          {
            title: "Beneficiaries (Type and Number of Male and Female): ",
            newlineAfterValue: true,
            value: stripLeadingRoman((data as any).beneficiaries ?? ""),
          },
          {
            title: "Total Cost: ",
            value: formatCurrency(parseInt(data.totalCost || "0")),
          },
          {
            title: "Source of fund: ",
            value: stripLeadingRoman(data.sourceOfFund),
          },
          {
            title: "Rationale: ",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.rationale),
          },
          {
            title: "Objectives: ",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.objectives),
          },
          {
            title: "Program/Project Expected Output: ",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.expectedOutput),
          },
          {
            title:
              "Description, Strategies and Methods (Activities / Schedule): ",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.description),
          },
          {
            title: "Financial Plan: ",
            newlineAfterValue: true,
            value: (
              <div style={{ marginTop: "6px", display: "flex", justifyContent: "center", width: "100%" }}>
                <FinancialPlanTable value={data.financialPlan} />
              </div>
            ),
          },
          {
            title:
              "Functional Relationships with the Partner Agencies (Duties / Tasks of the Partner Agencies): ",
            newlineAfterValue: true,
            value: stripLeadingRoman(data.partners),
          },
          {
            title: "Monitoring and Evaluation Mechanics / Plan:",
            newlineAfterValue: true,
          },
        ];
  return (
    <table className="bsuFormChild compact external-event-main-content" style={{ pageBreakInside: "auto", breakInside: "auto" }}>
            <ColSizeGen colSize={2} percentage="50%" />
            <tbody>
              <tr>
                <td colSpan={2} className="fontSet" style={{ padding: "10px 8px" }}>
                  <div style={{ marginBottom: "10px" }}>
                    <CheckBoxText
                      romaize
                      message="Extension Service Program/Project/Activity is requested by clients."
                      checked={
                        data.externalServiceType?.includes(
                          "Extension Service Program/Project/Activity is requested by clients."
                        ) ?? false
                      }
                    />
                  </div>
                  <div style={{ marginBottom: "10px" }}>
                    <CheckBoxText
                      romaize
                      message="Extension Service Program/Project/Activity is Department's initiative."
                      checked={
                        data.externalServiceType?.includes(
                          "Extension Service Program/Project/Activity is Department's initiative."
                        ) ?? false
                      }
                    />
                  </div>
                </td>
              </tr>
              <tr>
                <td colSpan={2} className="fontSet" style={{ padding: "10px 8px", borderTop: "1px solid #000" }}>
                  <FlexBox justifyContent="flex-start" gap="30px" style={{ paddingLeft: "10px" }}>
                    <CheckBoxText
                      romaize
                      message="Program"
                      checked={
                        data?.eventProposalType?.includes("Program") ?? false
                      }
                    />
                    <CheckBoxText
                      romaize
                      message="Project"
                      checked={
                        data?.eventProposalType?.includes("Project") ?? false
                      }
                    />
                    <CheckBoxText
                      romaize
                      message="Activity"
                      checked={
                        data?.eventProposalType?.includes("Activity") ?? false
                      }
                    />
                  </FlexBox>
                </td>
              </tr>
              <tr>
                <td colSpan={2} className="fontSet" style={{ pageBreakInside: "auto", breakInside: "auto" }}>
                  <RomanListValues
                    romaize
                    marginBetween="10px"
                    list={mainList as any}
                  />
                  <div className="monitoring-evaluation-section">
                    <div className="inner-form-table" style={{ marginTop: "6px" }}>
                      <EvaluationMechanicsTable
                        data={safeParseJsonObject(data.evaluationMechanicsPlan)}
                      />
                    </div>
                  </div>
                  <RomanListValues
                    romaize
                    start={(mainList.length + 1) as number}
                    list={[
                      {
                        title: "Sustainability Plan: ",
                        newlineAfterValue: true,
                        value: stripLeadingRoman(data.sustainabilityPlan),
                      },
                    ]}
                  />
                </td>
              </tr>
            </tbody>
          </table>
        );
      })()}
      {/* Signatories (added to match Internal form) */}
      <table className="bsuFormChild internal-event-table-with-top-border" style={{ borderTop: "1px solid black" }}>
        <ColSizeGen colSize={2} percentage="50%" />
        <tbody>
          <tr>
            <BSUTemplateSigning
              romaize
              colspan={1}
              upperMessage="Prepared By:"
              designation={data?.signatoriesId?.preparedTitle}
              placeHolder={data?.signatoriesId?.preparedBy}
            />
            <BSUTemplateSigning
              romaize
              colspan={1}
              upperMessage="Reviewed By:"
              designation={data?.signatoriesId?.reviewedTitle}
              placeHolder={data?.signatoriesId?.reviewedBy}
            />
          </tr>
          <tr>
            <BSUTemplateSigning
              colspan={1}
              upperMessage="Recommending approval:"
              designation={data?.signatoriesId?.recommendingSignatory1}
              placeHolder={data?.signatoriesId?.recommendingApproval1}
              romaize
            />
            <BSUTemplateSigning
              colspan={1}
              upperMessage="Recommending approval:"
              designation={data?.signatoriesId?.recommendingSignatory2}
              placeHolder={data?.signatoriesId?.recommendingApproval2}
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

export default ExternalEventForm;
