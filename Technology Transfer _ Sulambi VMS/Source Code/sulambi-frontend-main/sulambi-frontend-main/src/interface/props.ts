import {
  ButtonProps,
  DividerProps,
  SelectChangeEvent,
  TextFieldProps,
} from "@mui/material";
import { CSSProperties, ReactNode } from "react";
import { CheckBoxDataType, RadioListDataType } from "./types";

export interface CustomButtonProps extends ButtonProps {
  label?: string;
  hoverSx?: CSSProperties;
  hoverWhite?: boolean;
}

export interface PrimaryButtomProps extends CustomButtonProps {
  label: string;
  icon?: ReactNode;
  startIcon?: ReactNode;
}

export type CustomInputProps = TextFieldProps & {
  startIcon?: ReactNode;
  endIcon?: ReactNode;
  forceEnd?: boolean;
  width?: string;
  flex?: number;
  isMultiUpload?: boolean;
};

export interface CustomDropDownInputProps {
  label?: string;
  initialValue?: any;
  width?: string;
  flex?: number;
  error?: boolean;
  disabled?: boolean;
  onChange?: (event: SelectChangeEvent) => void;
  menu: {
    key: string;
    value: any;
  }[];
}

export interface CustomDividerProps extends DividerProps {
  color?: string;
  thickness?: string;
  width?: string;
  mt?: string;
  mb?: string;
}

export interface LineButtonProps {
  style?: CSSProperties;
  label?: string;
  active?: boolean;
  onClick?: (event: any) => void;
}

export interface MediaCardProps {
  cardTitle?: string;
  location?: string;
  children?: ReactNode;
  contentHeight?: string;
  height?: string;
  width: string;
  onViewDetails?: () => void;
  onVolunteer?: () => void;
}

export interface HorizontalCarouselProps {
  boxes: ReactNode[];
}

export interface BsuTemplateHeaderProps {
  reference?: string;
  effectivityDate?: string;
  revisionNumber?: string;
  formTitle?: string;
  children?: ReactNode;
  romaize?: boolean;
  containerClassName?: string;
  logoSrc?: string;
  logoAlt?: string;
  eventTypeSelection?: {
    program?: boolean;
    project?: boolean;
    activity?: boolean;
  };
}

export interface ColSizeGenProps {
  colSize: number;
  percentage: string;
}

export interface PopUpModalProps {
  header: string;
  open: boolean;
  subHeader?: string;
  children?: ReactNode;
  minHeight?: string;
  minWidth?: string;
  maxHeight?: string;
  maxWidth?: string;
  width?: string;
  smallHeader?: boolean;
  disableBGShadow?: boolean;
  hideCloseButton?: boolean;
  zval?: number;
  setOpen?: (state: boolean) => void;
  onClose?: () => void;
}

export interface MembershipAppFormProps {
  eventId?: number;
  dataLoader?: boolean;
  hideSubmit?: boolean;
  viewOnly?: boolean;
  componentsBeforeSubmit?: ReactNode;
  open: boolean;
  setOpen?: (state: boolean) => void;
  onSubmit?: () => void;
}

export interface ConfirmModalProps {
  title?: string;
  message: string;
  open: boolean;
  acceptText?: string;
  declineText?: string;
  setOpen?: (state: boolean) => void;
  onCancel?: () => void;
  onAccept?: () => void;
  zindex?: number;
}

export interface CustomCheckboxProps {
  values?: any[];
  checkboxData: CheckBoxDataType[];
  onChange?: (data: any) => void;
}

export interface CustomRadioProps {
  value?: any;
  viewOnly?: boolean;
  radioListData: RadioListDataType[];
  rowDirection?: boolean;
  onChange?: (value: any) => void;
}

export interface DashboardCardProps {
  value: string | number;
  label: string;
  icon?: ReactNode;
  increase?: string;
  onClick?: () => void;
}

export interface ChipProps {
  label: string;
  color?: string;
  bgcolor: string;
}
