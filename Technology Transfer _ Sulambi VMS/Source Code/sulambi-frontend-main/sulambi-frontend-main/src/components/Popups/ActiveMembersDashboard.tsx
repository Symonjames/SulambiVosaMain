import { useEffect, useState } from "react";
import SelectionCard from "../Cards/SelectionCard";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import { getDashboardMemberDetails } from "../../api/dashboard";
import { Box, Typography } from "@mui/material";

interface Props {
  open: boolean;
  setOpen?: (state: boolean) => void;
}

const ActiveMembersDashboard: React.FC<Props> = ({ open, setOpen }) => {
  const [memberDetails, setMemberDetails] = useState<any>({});

  useEffect(() => {
    if (open)
      getDashboardMemberDetails().then((response) => {
        setMemberDetails(response.data.data);
      });
  }, [open]);

  return (
    <PopupModal
      header="Active Members Details"
      open={open}
      setOpen={setOpen}
      maxHeight="50vh"
    >
      <Box maxHeight="40vh" overflow="auto">
        <FlexBox flexDirection="column" rowGap="10px">
          {Object.keys(memberDetails).length === 0 && (
            <Typography textAlign="center">No Active members</Typography>
          )}
          {Object.keys(memberDetails).map((name) => {
            return (
              <SelectionCard
                hideActions
                header={name}
                subheader={
                  <Typography
                    fontWeight="bold"
                    color="green"
                    variant="subtitle2"
                  >
                    Total Number of Events Participated:{" "}
                    {memberDetails[name] ?? 0}
                  </Typography>
                }
              />
            );
          })}
        </FlexBox>
      </Box>
    </PopupModal>
  );
};

export default ActiveMembersDashboard;
