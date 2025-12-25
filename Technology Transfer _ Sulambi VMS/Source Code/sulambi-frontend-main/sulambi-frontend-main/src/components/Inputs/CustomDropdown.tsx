import { Box, FormControl, InputLabel, MenuItem } from "@mui/material";
import { CustomDropDownInputProps } from "../../interface/props";
import Select from "@mui/material/Select";

const CustomDropdown: React.FC<CustomDropDownInputProps> = ({
  label,
  disabled,
  initialValue,
  error,
  menu,
  width,
  flex,
  onChange,
}) => {
  return (
    <Box width={width ?? "auto"} sx={{ flex: flex }}>
      <FormControl size="small" fullWidth>
        <InputLabel>{label}</InputLabel>
        <Select
          disabled={disabled}
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          value={initialValue || ''}
          label={label}
          onChange={onChange}
          error={error}
          MenuProps={{
            PaperProps: {
              style: {
                maxHeight: "300px",
                zIndex: 10002,
              },
              sx: {
                zIndex: '10002 !important',
              },
            },
            disablePortal: false,
            style: {
              zIndex: 10002,
            },
            sx: {
              zIndex: '10002 !important',
              '& .MuiPaper-root': {
                zIndex: '10002 !important',
              },
            },
          }}
        >
          {menu.map(({ key, value }, index) => (
            <MenuItem key={index} value={value}>{key}</MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default CustomDropdown;
