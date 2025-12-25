import React, { useState } from "react";

// A simplified ColSizeGen that respects live widths
const ColSizeGen = ({ widths }: { widths: (string | number)[] }) => (
  <colgroup>
    {widths.map((w, i) => (
      <col key={i} style={{ width: typeof w === "number" ? `${w}px` : w }} />
    ))}
  </colgroup>
);

export default function EditableTableDemo() {
  // Each table's adjustable column widths
  const [workPlanWidths, setWorkPlanWidths] = useState([
    220, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35,
  ]);
  const [financeWidths, setFinanceWidths] = useState([320, 80, 80, 100, 100]);
  const [evalWidths, setEvalWidths] = useState([
    160, 180, 120, 140, 120, 140, 160, 160,
  ]);

  // Demo data
  const workPlanData = [
    {
      activities: "asdf",
      act_1: "dsfa",
      act_2: "afs",
      act_3: "afsd",
      act_4: "dsafa",
      act_5: "fdsa",
      act_6: "fasda",
      act_7: "asdf",
      act_8: "asdf",
      act_9: "asdf",
      act_10: "sadfa",
      act_11: "asdf",
      act_12: "",
    },
    {
      activities: "dsafa",
      act_1: "aafd",
      act_2: "afd",
      act_3: "ff",
      act_4: "ff",
      act_5: "f",
      act_6: "f",
      act_7: "f",
      act_8: "f",
      act_9: "f",
      act_10: "f",
      act_11: "f",
      act_12: "f",
    },
  ];

  const financialData = [
    { item: "sadfa", qty: "323", unit: "sdfa", unitCost: "3223", total: "45233" },
  ];

  const evaluationData = [
    {
      specificObjective: "asdfa",
      performanceIndicator: "asdf",
      baselineData: "adsf",
      performanceTarget: "asdf",
      dataSource: "asdf",
      collectionMethod: "adsfad",
      frequencyOfCollection: "asdf",
      personResponsible: "asdf",
    },
  ];

  // Simple helper to render sliders
  const WidthSliders = ({
    widths,
    setWidths,
  }: {
    widths: number[];
    setWidths: (v: number[]) => void;
  }) => (
    <div style={{ marginBottom: "10px" }}>
      {widths.map((w, i) => (
        <div key={i} style={{ display: "inline-block", marginRight: "10px" }}>
          <label style={{ fontSize: "10pt" }}>
            Col {i + 1}:&nbsp;
            <input
              type="number"
              min={30}
              max={500}
              value={w}
              onChange={(e) => {
                const val = Number(e.target.value);
                const newWidths = [...widths];
                newWidths[i] = val;
                setWidths(newWidths);
              }}
              style={{ width: "60px" }}
            />
            px
          </label>
        </div>
      ))}
    </div>
  );

  return (
    <div style={{ padding: "20px" }}>
      {/* ---------- WORK PLAN ---------- */}
      <h3>Work Plan (Timeline of Activities / Gantt Chart)</h3>
      <WidthSliders widths={workPlanWidths} setWidths={setWorkPlanWidths} />
      <table className="bsuFormChild">
        <ColSizeGen widths={workPlanWidths} />
        <thead>
          <tr>
            <th>Activities</th>
            {[...Array(12)].map((_, i) => (
              <th key={i + 1}>{i + 1}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {workPlanData.map((row, idx) => (
            <tr key={idx}>
              <td>{row.activities}</td>
              {[...Array(12)].map((_, i) => (
                <td key={i}>{row[`act_${i + 1}` as keyof typeof row]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* ---------- FINANCIAL REQUIREMENTS ---------- */}
      <h3>Financial Requirements and Source of Funds</h3>
      <WidthSliders widths={financeWidths} setWidths={setFinanceWidths} />
      <table className="bsuFormChild">
        <ColSizeGen widths={financeWidths} />
        <thead>
          <tr>
            <th>Item Description</th>
            <th>Quantity</th>
            <th>Unit</th>
            <th>Unit Cost</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {financialData.map((row, idx) => (
            <tr key={idx}>
              <td>{row.item}</td>
              <td>{row.qty}</td>
              <td>{row.unit}</td>
              <td>{row.unitCost}</td>
              <td>{row.total}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* ---------- MONITORING & EVALUATION ---------- */}
      <h3>Monitoring and Evaluation Mechanics / Plan</h3>
      <WidthSliders widths={evalWidths} setWidths={setEvalWidths} />
      <table className="bsuFormChild">
        <ColSizeGen widths={evalWidths} />
        <thead>
          <tr>
            <th>Objectives</th>
            <th>Performance Indicators</th>
            <th>Baseline Data</th>
            <th>Performance Target</th>
            <th>Data Source</th>
            <th>Collection Method</th>
            <th>Frequency of Data Collection</th>
            <th>Office/Persons Responsible</th>
          </tr>
        </thead>
        <tbody>
          {evaluationData.map((row, idx) => (
            <tr key={idx}>
              <td>{row.specificObjective}</td>
              <td>{row.performanceIndicator}</td>
              <td>{row.baselineData}</td>
              <td>{row.performanceTarget}</td>
              <td>{row.dataSource}</td>
              <td>{row.collectionMethod}</td>
              <td>{row.frequencyOfCollection}</td>
              <td>{row.personResponsible}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

