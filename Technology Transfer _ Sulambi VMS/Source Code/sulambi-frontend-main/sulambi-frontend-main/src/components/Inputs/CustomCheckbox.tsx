import Checkbox from "@mui/material/Checkbox";
import { FormControl, FormControlLabel } from "@mui/material";
import { CustomCheckboxProps } from "../../interface/props";

const CustomCheckbox: React.FC<CustomCheckboxProps> = ({
  checkboxData,
  onChange,
  values,
}) => {
  return (
    <FormControl
      size="small"
      sx={{ padding: "10px", color: "gray", rowGap: "10px" }}
    >
      {checkboxData.length > 0 ? (
        checkboxData.map((data, index) => {
          return (
            <FormControlLabel
              key={index}
              label={data.label}
              control={<Checkbox checked={values?.includes(data.label)} />}
              onChange={() => onChange && onChange(data.label)}
            />
          );
        })
      ) : (
        <></>
      )}
    </FormControl>
  );
};

export default CustomCheckbox;
