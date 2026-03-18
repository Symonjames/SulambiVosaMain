import { useEffect, useState } from "react";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import { analyzeExternalEvent, analyzeInternalEvent } from "../../api/events";
import { AnalysisResultType } from "../../interface/types";
import SelectionCard from "../Cards/SelectionCard";

interface Props {
  eventId: number;
  eventType: "external" | "internal";
  open: boolean;
  setOpen?: (open: boolean) => void;
  zval?: number;
}

// score below than this will be marked as red
const THRESHOLD = 0.3;

const LatentAnalysisList: React.FC<Props> = (props) => {
  const { open, eventId, eventType, setOpen, zval } = props;
  const [analysisResult, setAnalysisResult] = useState<AnalysisResultType>();

  useEffect(() => {
    if (open) {
      if (eventType === "external")
        analyzeExternalEvent(eventId).then((response) => {
          setAnalysisResult(response.data.analysis);
        });

      if (eventType === "internal")
        analyzeInternalEvent(eventId).then((response) => {
          setAnalysisResult(response.data.analysis);
        });
    }
  }, [open]);

  return (
    <PopupModal
      header="Latent Semantic Analysis"
      subHeader="Below are the ranking of topics suggested by the participants"
      open={open}
      minHeight="60vh"
      setOpen={setOpen}
      zval={zval ?? 7}
    >
      <FlexBox
        flexDirection="column"
        rowGap="10px"
        marginTop="20px"
        maxHeight="50vh"
        overflow="auto"
      >
        {Object.keys(analysisResult ?? {})
          .sort(
            (a: string, b: string) =>
              (analysisResult as any)[b] - (analysisResult as any)[a]
          )
          .map((context: string, index: number) => (
            <SelectionCard
              key={index}
              hideActions
              header={context}
              subheader={
                <>
                  Similarity Score:{" "}
                  <b
                    style={{
                      color:
                        (analysisResult as any)[context] >= THRESHOLD
                          ? "green"
                          : "red",
                    }}
                  >
                    {Math.round(
                      ((analysisResult as any)[context] + Number.EPSILON) * 100
                    ) / 100}
                  </b>
                </>
              }
            />
          ))}
      </FlexBox>
    </PopupModal>
  );
};

export default LatentAnalysisList;
