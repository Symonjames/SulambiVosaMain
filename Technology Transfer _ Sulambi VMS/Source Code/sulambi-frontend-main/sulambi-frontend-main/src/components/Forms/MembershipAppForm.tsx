import { MembershipAppFormProps } from "../../interface/props";
import PrimaryButton from "../Buttons/PrimaryButton";
import FlexBox from "../FlexBox";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import PopupModal from "../Modal/PopupModal";
import SendIcon from "@mui/icons-material/Send";
import EmailIcon from "@mui/icons-material/Email";
import PersonIcon from "@mui/icons-material/Person";
import PasswordIcon from "@mui/icons-material/Password";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import KeyIcon from "@mui/icons-material/Key";
import CloseIcon from "@mui/icons-material/Close";

import { IconButton } from "@mui/material";
import { useContext, useEffect, useState } from "react";
import FormGeneratorTemplate from "./FormGeneratorTemplate";
import { register } from "../../api/auth";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

const isValidEmail = (email: string) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

function isValidPassword(
  password: string,
  options: {
    minLength?: number;
    maxLength?: number;
    requireUppercase?: boolean;
    requireLowercase?: boolean;
    requireNumbers?: boolean;
    requireSpecialChars?: boolean;
  } = {}
): boolean {
  const {
    minLength = 8,
    maxLength = 128,
    requireUppercase = true,
    requireLowercase = true,
    requireNumbers = true,
    requireSpecialChars = true,
  } = options;

  if (password.length < minLength || password.length > maxLength) {
    return false;
  }

  if (requireUppercase && !/[A-Z]/.test(password)) {
    return false;
  }

  if (requireLowercase && !/[a-z]/.test(password)) {
    return false;
  }

  if (requireNumbers && !/[0-9]/.test(password)) {
    return false;
  }

  if (requireSpecialChars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return false;
  }

  return true;
}

const MembershipAppForm: React.FC<MembershipAppFormProps> = ({
  dataLoader,
  viewOnly,
  componentsBeforeSubmit,
  hideSubmit,
  open,
  onSubmit,
  setOpen,
}) => {
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const [fieldErrors, setFieldErrors] = useState<string[]>([]);

  // dynamic form field changer
  const [showQ7, setShowQ7] = useState(false);
  const [showQ10, setShowQ10] = useState(false);
  const [otherWeekdays, setOtherWeekdays] = useState(false);
  const [otherWeekends, setOtherWeekends] = useState(false);
  const [stateRefresh, setStateRefresh] = useState(0);

  const { formData, setFormData } = useContext(FormDataContext);

  // Ensure form is blank on first mount (prevents retained username/password)
  useEffect(() => {
    if (!dataLoader) setFormData({});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!dataLoader) setFormData({});
  }, [open]);

  const submitAction = async () => {
    setFieldErrors([]);

    // format validation
    if (!isValidEmail(formData["email"])) {
      setFieldErrors(["email"]);
      showSnackbarMessage("Email Format not valid", "error");
      return;
    }

    if (
      !isValidPassword(formData["password"], {
        minLength: 8,
        requireUppercase: true,
      })
    ) {
      setFieldErrors(["password"]);
      showSnackbarMessage(
        "The password be longer than 8 characters and has at least one uppercase",
        "error"
      );
      return;
    }

    try {
      await register(formData);
      showSnackbarMessage("Successfully registered new member!", "success");
      setOpen && setOpen(false);
      onSubmit && onSubmit();
    } catch (err: any) {
      if (err.response.data) {
        const message = err.response.data.message;
        const errors = err.response.data.fieldError ?? [];

        setFieldErrors(errors);
        showSnackbarMessage(`Error Occured: ${message}`, "error");
      } else {
        showSnackbarMessage(
          "An error Occured when registering membership",
          "error"
        );
      }
    }
  };

  return (
    <>
      <PopupModal
        header="Membership Application Form"
        subHeader="This Form will serve as your application for membership to the
          Sulambi Volunteers Organization"
        open={open}
        setOpen={setOpen}
        width="25vw"
        maxHeight="80vh"
      >
        <form
          style={{
            maxHeight: "50vh",
            overflowY: "auto",
            scrollbarWidth: "thin",
          }}
        >
          <FlexBox
            flexDirection="column"
            alignItems="center"
            marginBottom="20px"
            rowGap="15px"
          >
            <FormGeneratorTemplate
              viewOnly={viewOnly}
              dataLoader={dataLoader}
              enableAutoFieldCheck
              forceRefresh={stateRefresh}
              fieldErrors={fieldErrors}
              template={[
                { type: "divider" },
                [
                  {
                    id: "email",
                    required: true,
                    type: "text",
                    message: "Email Address",
                    icon: <EmailIcon />,
                  },
                ],
                [
                  {
                    id: "affiliation",
                    type: "text",
                    message: "Organization/Affiliation",
                    required: true,
                  },
                  {
                    id: "applyingAs",
                    required: true,
                    type: "dropdown",
                    message: "Applying as",
                    menu: [
                      { value: "", key: "-- Select One --" },
                      { value: "New membership", key: "New membership" },
                      {
                        value: "Renewal of Membership",
                        key: "Renewal of Membership",
                      },
                      { value: "Alumni Membership", key: "Alumni Membership" },
                    ],
                  },
                ],
                [
                  {
                    id: "volunterismExperience",
                    required: true,
                    type: "dropdown",
                    message: "Volunterism experience",
                    menu: [
                      {
                        key: "Has prior volunteerism experience",
                        value: "yes",
                      },
                      {
                        key: "Has no prior volunteerism experience",
                        value: "no",
                      },
                    ],
                    onUse: (event) => {
                      setShowQ7(event.target.value === "yes");
                      setShowQ10(event.target.value === "no");
                      setStateRefresh(stateRefresh + 1);
                    },
                  },
                ],
                [
                  {
                    id: "weekdaysTimeDevotion",
                    hidden: otherWeekdays,
                    hideOnView: true,
                    required: true,
                    type: "dropdown",
                    message:
                      "How much time can you devote for volunteering activities on weekdays?",
                    menu: [
                      {
                        key: "Can you devote 1-4 hours on weekdays",
                        value: "1-4 hours",
                      },
                      {
                        key: "Can you devote 5-8 hours on weekdays",
                        value: "5-8 hours",
                      },
                      {
                        key: "Can you devote 8 hours or more on weekdays",
                        value: "8 hours or more",
                      },
                      {
                        key: "Other...",
                        value: "other",
                      },
                    ],
                    onUse: (event) => {
                      if (event.target.value === "other") {
                        setOtherWeekdays(!otherWeekdays);
                        setStateRefresh(stateRefresh + 1);
                      }
                    },
                  },
                  {
                    id: "weekdaysTimeDevotion",
                    required: true,
                    type: "text",
                    hidden: !otherWeekdays,
                    showOnView: true,
                    message:
                      "How much time can you devote for volunteering activities on weekdays?",
                    endIcon: (
                      <IconButton
                        onClick={() => {
                          setOtherWeekdays(!otherWeekdays);
                          setStateRefresh(stateRefresh + 1);
                        }}
                      >
                        <CloseIcon />
                      </IconButton>
                    ),
                  },
                ],
                [
                  {
                    id: "weekendsTimeDevotion",
                    hidden: otherWeekends,
                    hideOnView: true,
                    required: true,
                    type: "dropdown",
                    message:
                      "How much time can you devote for volunteering activities on weekends?",
                    menu: [
                      {
                        key: "Can you devote 1-4 hours on weekends",
                        value: "1-4 hours",
                      },
                      {
                        key: "Can you devote 5-8 hours on weekends",
                        value: "5-8 hours",
                      },
                      {
                        key: "Can you devote 8 hours or more on weekends",
                        value: "8 hours or more",
                      },
                      {
                        key: "Other...",
                        value: "other",
                      },
                    ],
                    onUse: (event) => {
                      if (event.target.value === "other") {
                        setOtherWeekends(!otherWeekends);
                        setStateRefresh(stateRefresh + 1);
                      }
                    },
                  },
                  {
                    id: "weekendsTimeDevotion",
                    required: true,
                    showOnView: true,
                    type: "text",
                    hidden: !otherWeekends,
                    message:
                      "How much time can you devote for volunteering activities on weekends?",
                    endIcon: (
                      <IconButton
                        onClick={() => {
                          setOtherWeekends(!otherWeekends);
                          setStateRefresh(stateRefresh + 1);
                        }}
                      >
                        <CloseIcon />
                      </IconButton>
                    ),
                  },
                ],

                [
                  {
                    id: "areasOfInterest",
                    required: true,
                    type: "checkbox",
                    message:
                      "What areas or interests do you want to volunteer in? Check the area(s) that interest you.",
                    selectionQuestion: [
                      {
                        initialValue: false,
                        label:
                          "Education and Literacy (Peace education, Human rights, Legal counseling/advice, IT literacy, Labor and Employment / Workers' education, Socio-cultural, history and heritage - related activities, Arts, IEC Materials Development, Urban Planning, Rural Development)",
                      },
                      {
                        initialValue: false,
                        label:
                          "Health and Wellness (Food and nutrition, Health and sanitation, Maternal and child-care, Guidance counseling)",
                      },
                      {
                        initialValue: false,
                        label:
                          "Environment and Disaster Mitigation (Cleanup drives, Tree-planting, Clean and green activities, Solid Waste Management)",
                      },
                      {
                        initialValue: false,
                        label:
                          "Livelihood (Agriculture, Technical-vocational / skills training, Nursery and vegetable garden establishment, Business / Financial Planning, Small construction works, Engineering design consultancy)",
                      },
                      {
                        initialValue: false,
                        label:
                          "Outreach (Medical mission, Dental mission, Optical mission, Blood donation, Visit to orphanages, Visit to prison camps, Visit to rehabilitation center, Relief operation, Gift-giving activity, Sports and Recreation)",
                      },
                      {
                        initialValue: false,
                        label: "Gender and Development (GAD)",
                      },
                    ],
                  },
                ],

                //////////////////////////////
                //  VOLUNTERISM EXPERIENCE  //
                //////////////////////////////
                {
                  type: "section",
                  message: "Proof of Volunteerism Experiences",
                  hidden: !showQ7,
                },
                {
                  id: "volunteerExpQ1",
                  type: "textQuestion",
                  message:
                    "What volunteering activities of Sulambi VOSA last academic year did you join?",
                  hidden: !showQ7,
                },
                {
                  id: "volunteerExpQ2",
                  type: "textQuestion",
                  message:
                    "What volunteering activities did you join outside Sulambi VOSA and/or the University?",
                  hidden: !showQ7,
                },
                [
                  {
                    id: "volunteerExpProof",
                    type: "text",
                    flex: 1,
                    message:
                      "Upload proof for the volunteering activities you joined outside (gdrive link)",
                    hidden: !showQ7,
                  },
                ],

                ////////////////////////////
                //  REASONS FOR APPLYING  //
                ////////////////////////////
                {
                  type: "section",
                  message: "Reason(s) for applying",
                  hidden: !showQ10,
                },
                {
                  id: "reasonQ1",
                  type: "textQuestion",
                  message: "Why do you want to become a member?",
                  hidden: !showQ10,
                },
                {
                  id: "reasonQ2",
                  type: "textQuestion",
                  message: "What can you contribute to the organization?",
                  hidden: !showQ10,
                },

                ///////////////////////
                //  ACCOUNT DETAILS  //
                ///////////////////////
                {
                  type: "section",
                  message: "Account Details",
                },
                [
                  {
                    id: "username",
                    required: true,
                    type: "text",
                    message: "Set Account Username",
                    icon: <AccountCircleIcon />,
                  },
                  {
                    id: "password",
                    required: true,
                    type: "password",
                    message: "Set Account Password",
                    icon: <KeyIcon />,
                  },
                ],

                ////////////////////////
                //  PERSONAL DETAILS  //
                ////////////////////////
                {
                  type: "section",
                  message: "Personal Details",
                },
                [
                  {
                    id: "fullname",
                    required: true,
                    type: "text",
                    message: "Name (Lastname, Firstname, Middle Initial)",
                    icon: <PersonIcon />,
                  },
                ],
                [
                  {
                    id: "email",
                    flex: 2,
                    type: "text",
                    message: "GSuite Email",
                    icon: <EmailIcon />,
                  },
                  {
                    id: "srcode",
                    flex: 1,
                    type: "text",
                    required: true,
                    message: "SR-Code",
                    icon: <PasswordIcon />,
                  },
                ],
                [
                  {
                    id: "birthday",
                    flex: 5,
                    required: true,
                    type: "text",
                    message: "Birth Date (Example: January 7, 2023)",
                    icon: <CalendarMonthIcon />,
                  },
                  {
                    id: "age",
                    required: true,
                    type: "number",
                    message: "Age",
                    onUse: (event: any) => {
                      // Enforce max 2 digits (0-99) and digits only
                      const raw = String(event?.target?.value ?? "");
                      const digitsOnly = raw.replace(/\D+/g, "").slice(0, 2);
                      setFormData({ ...formData, age: digitsOnly });
                    },
                  },
                  {
                    id: "sex",
                    required: true,
                    type: "dropdown",
                    message: "Sex",
                    menu: [
                      { key: "Male", value: "male" },
                      { key: "Female", value: "female" },
                    ],
                  },
                ],
                [
                  {
                    id: "campus",
                    required: true,
                    type: "text",
                    message: "Campus",
                  },
                  {
                    id: "collegeDept",
                    required: true,
                    type: "text",
                    message: "College Department",
                  },
                ],
                [
                  {
                    id: "yrlevelprogram",
                    required: true,
                    type: "text",
                    message: "Year level & Program",
                  },
                  {
                    id: "address",
                    required: true,
                    type: "text",
                    message: "Address",
                  },
                ],
                [
                  {
                    id: "contactNum",
                    required: true,
                    type: "text",
                    message: "Contact No.",
                  },
                  {
                    id: "fblink",
                    required: true,
                    type: "text",
                    message: "Facebook Link",
                  },
                ],
                [
                  {
                    id: "bloodDonation",
                    flex: 3,
                    required: true,
                    type: "dropdown",
                    message: "Blood Donation",
                    menu: [
                      { key: "I'm eligible to donate.", value: 0 },
                      { key: "I'm willing to donate.", value: 1 },
                      {
                        key: "I'm willing but I am not aware if I'm eligible.",
                        value: 2,
                      },
                      { key: "I'm not willing.", value: 3 },
                    ],
                  },
                  {
                    id: "bloodType",
                    required: true,
                    type: "text",
                    message: "Blood Type",
                  },
                ],

                //////////////////////
                //  FEE COLLECTION  //
                //////////////////////
                { type: "section", message: "Fee Collection" },
                [
                  {
                    type: "label",
                    message: `As stipulated in the organizations Constitution and By-Laws, a
              membership fee of fifty pesos (Php 50) shall be collected from the
              members every semester. Kindly send an email to Sulambi (sulambivosa@g.batstate-u.edu.ph) for payment details. This may be paid through any of the
              following options:`,
                  },
                ],
                [
                  {
                    id: "paymentOption",
                    type: "dropdown",
                    required: true,
                    message: "Payment Options",
                    menu: [
                      {
                        key: "One-time payment of Php 50.00 for the whole semester",
                        value:
                          "One-time payment of Php 50.00 for the whole semester",
                      },
                      {
                        key: "One-time payment of Php 100.00 for the whole academic year (2 semesters)",
                        value:
                          "One-time payment of Php 100.00 for the whole academic year (2 semesters)",
                      },
                    ],
                  },
                ],
              ]}
            />
          </FlexBox>
        </form>
        <FlexBox justifyContent="flex-end" marginTop="10px" gap="10px">
          {componentsBeforeSubmit}
          {!hideSubmit && (
            <PrimaryButton
              label="Submit"
              icon={<SendIcon />}
              size="small"
              onClick={submitAction}
            />
          )}
        </FlexBox>
      </PopupModal>
    </>
  );
};

export default MembershipAppForm;
