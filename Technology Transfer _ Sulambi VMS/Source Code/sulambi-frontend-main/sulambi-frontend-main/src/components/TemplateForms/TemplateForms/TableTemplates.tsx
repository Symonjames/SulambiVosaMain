import ColSizeGen from "./ColSizeGen";
import React from "react";

interface InnerFormTableTemplateProps {
  textAlign?: "center" | "left" | "justify" | "right";
  customColsize?: number;
  customPercentage?: number;
  customColWidths?: string[];
  customFlexSize?: number[];
  className?: string;
  headerPadding?: string;
  cellPadding?: string;
  fontSize?: string;
  tableWidth?: string;
  headerClassMap?: Record<string | number, string>;
  cellClassMap?: Record<string, string>;
  header: string[];
  dataKeys: any[];
  data: any[];
}

export const InnerFormTableTemplate: React.FC<InnerFormTableTemplateProps> = ({
  customColsize,
  customFlexSize,
  customPercentage,
  customColWidths,
  data,
  dataKeys,
  header,
  textAlign,
  className,
  headerPadding,
  cellPadding,
  fontSize,
  tableWidth,
  headerClassMap,
  cellClassMap,
}) => (
  <div style={{ width: "100%", overflowX: "auto", margin: "10px 0" }}>
    <table
      className={`bsuFormChild ${className ?? ""}`.trim()}
      style={{
        width: tableWidth ?? "100%",
        margin: "0",
        borderCollapse: "collapse",
        tableLayout: "fixed",
        fontSize: fontSize,
      }}
    >
      {Array.isArray(customColWidths) &&
      customColWidths.length === (customColsize ?? header.length) ? (
        <colgroup>
          {customColWidths.map((w, i) => (
            <col key={i} width={w} />
          ))}
        </colgroup>
      ) : (
        <ColSizeGen
          colSize={customColsize ?? header.length}
          percentage={`${customPercentage ?? 100 / header.length}%`}
        />
      )}
      <tbody>
        <tr>
          <td
            colSpan={customColsize ?? header.length}
            className="fontSet"
            style={{ padding: 0 }}
          ></td>
        </tr>
        <tr>
          {header.map((h, i) => (
            <td
              key={i}
              colSpan={customFlexSize ? (customFlexSize[i] ?? 1) : 1}
              className={`fontSet ${
                headerClassMap?.[i] ?? headerClassMap?.[h] ?? ""
              }`.trim()}
              style={{
                textAlign,
                fontWeight: "bold",
                padding: headerPadding ?? "6px 4px",
              }}
            >
              {h}
            </td>
          ))}
        </tr>
        {dataKeys.length === header.length ? (
          data.length === 0 ? (
            <tr>
              <td
                colSpan={customColsize ?? header.length}
                className="fontSet"
                style={{ textAlign, padding: 8 }}
              >
                (No data)
              </td>
            </tr>
          ) : (
            data.map((row, r) => (
              <tr key={r}>
                {dataKeys.map((k, c) => (
                  <td
                    key={c}
                    colSpan={customFlexSize ? (customFlexSize[c] ?? 1) : 1}
                    className={`fontSet ${cellClassMap?.[String(k)] ?? ""}`.trim()}
                    style={{
                      textAlign,
                      padding: cellPadding ?? "6px 4px",
                      borderTop: "1px solid #ccc",
                    }}
                  >
                    {row[k]}
                  </td>
                ))}
              </tr>
            ))
          )
        ) : null}
      </tbody>
    </table>
  </div>
);

export default InnerFormTableTemplate;














