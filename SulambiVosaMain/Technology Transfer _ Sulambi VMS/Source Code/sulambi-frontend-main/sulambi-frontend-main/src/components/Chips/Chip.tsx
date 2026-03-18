import { ChipProps } from "../../interface/props";

const Chip: React.FC<ChipProps> = ({ bgcolor, label, color }) => {
  return (
    <span
      style={{
        backgroundColor: bgcolor,
        color: color ?? "white",
        padding: "3px 6px",
        borderRadius: "20px",
        fontSize: "9pt",
      }}
    >
      {label}
    </span>
  );
};

export default Chip;
