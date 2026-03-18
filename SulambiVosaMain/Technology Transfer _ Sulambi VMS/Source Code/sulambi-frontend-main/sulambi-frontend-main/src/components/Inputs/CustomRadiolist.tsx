import { FormControl, FormControlLabel, RadioGroup } from "@mui/material";
import { CustomRadioProps } from "../../interface/props";
import Radio from "@mui/material/Radio";
import { useMediaQuery } from "react-responsive";

const CustomRadiolist: React.FC<CustomRadioProps> = ({
  rowDirection,
  radioListData,
  value,
  viewOnly,
  onChange,
}) => {
  const isMobile = useMediaQuery({
    query: "(max-width: 1224px)",
  });

  return (
    <FormControl
      size="small"
      sx={{
        padding: "10px",
        color: "gray",
        rowGap: "10px",
      }}
    >
      <RadioGroup
        value={value}
        onChange={(event: any, selectedValue: string) => {
          if (!viewOnly) onChange && onChange(selectedValue ?? event?.target?.value);
        }}
        sx={{
          display: "flex",
          ...(rowDirection
            ? {
                flexDirection: "row",
                justifyContent: isMobile ? "flex-start" : "space-around",
              }
            : {}),
        }}
      >
        {radioListData.length > 0 ? (
          radioListData.map((data) => {
            return (
              <FormControlLabel
                key={data.label}
                label={data.label}
                value={data.label}
                disabled={viewOnly}
                control={
                  <Radio
                    disabled={viewOnly}
                  />
                }
              />
            );
          })
        ) : (
          <></>
        )}
      </RadioGroup>
    </FormControl>
  );
};

export default CustomRadiolist;
