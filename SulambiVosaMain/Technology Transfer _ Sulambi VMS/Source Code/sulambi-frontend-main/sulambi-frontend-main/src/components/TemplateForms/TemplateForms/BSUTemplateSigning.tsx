import React from "react";
import FlexBox from "../FlexBox";

interface Props {
  upperMessage?: string;
  placeHolder?: string;
  designation?: string;
  colspan: number;
  romaize?: boolean;
}

const BSUTemplateSigning: React.FC<Props> = ({
  colspan,
  designation,
  placeHolder,
  upperMessage,
  romaize,
}) => {
  return (
    <td colSpan={colspan} style={{ 
      padding: "15px 20px",
      "@media print": {
        pageBreakInside: "avoid",
        breakInside: "avoid"
      }
    }}>
      <div className={romaize ? "fontSet" : ""} style={{ textAlign: "left", marginBottom: "8px" }}>
        {upperMessage}
      </div>
      <div 
        className={romaize ? "fontSet" : ""} 
        style={{ 
          textAlign: "center", 
          fontWeight: "bold", 
          marginBottom: "5px",
          marginTop: "12px"
        }}
      >
        {placeHolder}
      </div>
      <div 
        className={romaize ? "fontSet" : ""} 
        style={{ 
          textAlign: "center", 
          marginBottom: "8px",
          lineHeight: "1.2"
        }}
      >
        {designation}
      </div>
      <div 
        className={romaize ? "fontSet" : ""} 
        style={{ textAlign: "left", marginTop: "10px" }}
      >
        {designation !== "" && placeHolder !== "" ? "Date signed:" : ""}
      </div>
    </td>
  );
};

export default BSUTemplateSigning;
