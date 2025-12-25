import FlexBox from "../FlexBox";
import MenuButtonTemplate from "../Menu/MenuButtonTemplate";
import { MenuButtomTemplateItemType } from "../../interface/types";
import { Typography } from "@mui/material";

interface Props {
  header: any;
  subheader?: any;
  hideActions?: boolean;
  textAlign?: "center" | "left";
  enableMarginTop?: boolean;
  actions?: MenuButtomTemplateItemType[];
  onClickable?: () => void;
}

const SelectionCard: React.FC<Props> = (props) => {
  const {
    actions,
    enableMarginTop,
    header,
    textAlign,
    subheader,
    hideActions,
    onClickable,
  } = props;

  return (
    <FlexBox
      width="calc(100% - 20px)"
      bgcolor="#d9d9d9"
      alignItems="center"
      borderRadius="10px"
      padding="5px 10px"
      onClick={onClickable}
      sx={{
        textAlign,
        marginTop: enableMarginTop ? "10px" : "",
        cursor: "pointer",
        transition: "0.5s",
        ":hover": {
          backgroundColor: "gray",
        },
      }}
    >
      <FlexBox flexDirection="column" alignItems="flex-start" flexGrow={1}>
        <Typography fontWeight="bold">{header}</Typography>
        {subheader && <Typography variant="subtitle2">{subheader}</Typography>}
      </FlexBox>
      {!hideActions && (
        <FlexBox flexShrink={1}>
          <MenuButtonTemplate items={actions ?? []} />
        </FlexBox>
      )}
    </FlexBox>
  );
};

export default SelectionCard;
