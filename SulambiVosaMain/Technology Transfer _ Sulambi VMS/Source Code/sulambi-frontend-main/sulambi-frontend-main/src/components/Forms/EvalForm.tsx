import PopupModal from "../Modal/PopupModal";
import RawEvalForm from "./raw/RawEvalForm";

interface Props {
  open: boolean;
  zval?: number;
  setOpen?: (state: boolean) => void;
}

const EvalForm = ({ open, zval, setOpen }: Props) => {
  return (
    <PopupModal
      header="Evaluation Form "
      open={open}
      setOpen={setOpen}
      width="50vw"
      maxHeight="50vw"
      zval={zval ?? 6}
    >
      <RawEvalForm />
    </PopupModal>
  );
};

export default EvalForm;
