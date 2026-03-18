import { LineButtonProps } from "../../interface/props";

const LineButton: React.FC<LineButtonProps> = ({
  active,
  label,
  onClick,
  style,
}) => {
  return (
    <span
      className={`lineButton ${active ? "lineButtonActive" : ""}`}
      onClick={onClick}
      style={style}
    >
      {label}
    </span>
  );
};

export default LineButton;
