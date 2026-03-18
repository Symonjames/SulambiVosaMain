import { useContext, useEffect, useState } from "react";
import SelectionCard from "../Cards/SelectionCard";
import FlexBox from "../FlexBox";
import TextHeader from "../Headers/TextHeader";
import PopupModal from "../Modal/PopupModal";
import {
  getExternalEvaluations,
  getInternalEvaluations,
} from "../../api/evaluation";
import { EventEvalListType } from "../../interface/types";
import ArticleIcon from "@mui/icons-material/Article";
import NewspaperIcon from "@mui/icons-material/Newspaper";
import EvalForm from "../Forms/EvalForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

interface Props {
  open: boolean;
  selectedFormData: any;
  selectedFormType: "external" | "internal";
  setOpen: (state: boolean) => void;
}

const EvaluationList: React.FC<Props> = (props) => {
  const { open, selectedFormData, selectedFormType, setOpen } = props;
  const { setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);

  const [eventEvalList, setEventEvalList] = useState<EventEvalListType[]>([]);
  const [showEvalForm, setShowEvalForm] = useState(false);
  useEffect(() => {
    if (open) {
      if (selectedFormType === "external")
        getExternalEvaluations(selectedFormData.id).then((response) => {
          setEventEvalList(response.data.data);
        });

      if (selectedFormType === "internal")
        getInternalEvaluations(selectedFormData.id).then((response) => {
          setEventEvalList(response.data.data);
        });
    }
  }, [open]);

  return (
    <>
      <EvalForm open={showEvalForm} setOpen={setShowEvalForm} />
      <PopupModal
        header="Evaluation List"
        subHeader="Check submitted user evaluation here"
        maxHeight="70vh"
        open={open}
        setOpen={setOpen}
        zval={5}
      >
        <FlexBox flexDirection="column" rowGap="10px" marginTop="20px">
          {eventEvalList.length === 0 && (
            <TextHeader variant="h6" textAlign="center">
              No evaluation available
            </TextHeader>
          )}
          {eventEvalList.map((evalData) => {
            return (
              <SelectionCard
                header={evalData.requirements.fullname}
                subheader={evalData.requirements.srcode}
                actions={[
                  {
                    label: "View by Form",
                    icon: <ArticleIcon />,
                    onClick: () => {
                      evalData.evaluation.criteria = evalData.evaluation
                        .criteria
                        ? JSON.parse(evalData.evaluation.criteria)
                        : {};

                      setFormData(evalData.evaluation);
                      setShowEvalForm(true);
                    },
                  },
                  {
                    label: "View by Template",
                    icon: <NewspaperIcon />,
                    onClick: () => {
                      showSnackbarMessage(
                        "Currently under development",
                        "info"
                      );
                    },
                  },
                ]}
              />
            );
          })}
        </FlexBox>
      </PopupModal>
    </>
  );
};

export default EvaluationList;
