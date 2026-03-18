import { ColSizeGenProps } from "../../interface/props";

const ColSizeGen: React.FC<ColSizeGenProps> = ({ colSize, percentage }) => {
  const itemElements = [];
  for (let i = 0; i < colSize; i++)
    itemElements.push(<col key={i} width={percentage} />);

  return <colgroup>{itemElements}</colgroup>;
};

export default ColSizeGen;
