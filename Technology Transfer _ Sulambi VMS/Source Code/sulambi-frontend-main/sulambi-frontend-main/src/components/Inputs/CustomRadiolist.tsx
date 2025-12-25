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
                label={data.label}
                value={data.label}
                control={
                  <Radio
                    {...{
                      checked: viewOnly ? data.label === value : undefined,
                    }}
                  />
                }
                onChange={(event: any) => {
                  onChange && onChange(event.target.value);
                }}
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
