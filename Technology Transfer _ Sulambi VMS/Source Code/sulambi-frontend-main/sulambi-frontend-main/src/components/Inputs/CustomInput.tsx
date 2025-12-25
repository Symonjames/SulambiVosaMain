import { InputAdornment, TextField } from "@mui/material";
import { CustomInputProps } from "../../interface/props";

const CustomInput: React.FC<CustomInputProps> = (props) => {
  const { forceEnd, isMultiUpload, startIcon, endIcon, ...textFieldProps } = props;
  
  return (
    <TextField
      {...textFieldProps}
      size="small"
      sx={{ ...props.sx, width: props.width, flex: props.flex }}
      value={props.value}
      inputProps={{
        multiple: isMultiUpload,
      }}
      slotProps={
        startIcon
          ? {
              input: {
                startAdornment: (
                  <InputAdornment position={"start"}>
                    {startIcon}
                  </InputAdornment>
                ),
                ...(forceEnd && endIcon
                  ? {
                      endAdornment: (
                        <InputAdornment position={"end"}>
                          {endIcon}
                        </InputAdornment>
                      ),
                    }
                  : {}),
              },
            }
          : endIcon
          ? {
              input: {
                endAdornment: (
                  <InputAdornment position={"end"}>
                    {endIcon}
                  </InputAdornment>
                ),
              },
            }
          : {}
      }
    />
  );
};

export default CustomInput;
