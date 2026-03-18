import { Box } from "@mui/material";
import TextHeader from "../Headers/TextHeader";
import TextSubHeader from "../Headers/TextSubHeader";
import { DashboardCardProps } from "../../interface/props";
import FlexBox from "../FlexBox";

const DashboardCard: React.FC<DashboardCardProps> = ({
  label,
  value,
  icon,
  onClick,
}) => {
  return (
    <Box
      position="relative"
      width="18vw"
      height="100px"
      boxShadow="0 0 10px 1px gray"
      borderRadius="10px"
      padding="10px"
      display="grid"
      gridTemplateColumns="30% 70%"
      alignItems="center"
      onClick={onClick}
      sx={{
        cursor: onClick ? "pointer" : "",
        ":hover": onClick
          ? {
              bgcolor: "#e5e5e5",
            }
          : undefined,
      }}
    >
      <FlexBox
        height="100%"
        width="100%"
        alignItems="center"
        justifyContent="center"
        color="#c7c7c7"
      >
        {icon}
      </FlexBox>
      <Box>
        <TextHeader sx={{ fontSize: "25pt" }}>{value}</TextHeader>
        <TextSubHeader variant="body2">{label}</TextSubHeader>
      </Box>
    </Box>
  );
};

export default DashboardCard;
