import { ReactNode, useCallback, useContext, useEffect, useState } from "react";
import PrimaryButton from "../Buttons/PrimaryButton";
import FlexBox from "../FlexBox";
import PopupModal from "../Modal/PopupModal";
import SendIcon from "@mui/icons-material/Send";
import FormGeneratorTemplate, {
  FormGenTemplateProps,
} from "./FormGeneratorTemplate";
import { FormDataContext } from "../../contexts/FormDataProvider";
import {
  createExternalEvent,
  createInternalEvent,
  getOneEvent,
} from "../../api/events";
import { IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { SnackbarContext } from "../../contexts/SnackbarProvider";

interface Props {
  open: boolean;
  eventType?: [number, string];
  componentsBeforeSubmit?: ReactNode;
  hideSubmit?: boolean;
  viewOnly?: boolean;
  zval?: number;
  setOpen: (state: boolean) => void;
  onSubmit?: () => void;
  onClose?: () => void;
}

// TODO: Type of Extension not properly loaded

const EventProposalForm: React.FC<Props> = ({
  open,
  eventType,
  componentsBeforeSubmit,
  hideSubmit,
  viewOnly,
  zval,
  setOpen,
  onSubmit,
  onClose,
}) => {
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const { formData, setFormData, immutableSetFormData } =
    useContext(FormDataContext);

  const [showOtherSourceOfFund, setShowOtherSourceOfFund] = useState(false);
  const [fieldErrors, setFieldErrors] = useState([]);
  const [proposalType, setProposalType] = useState("");
  const [disableButton, setDisableButton] = useState(false);

  useEffect(() => {
    if (eventType) {
      const [eventId, type] = eventType;
      if (eventId && type != "") {
        getOneEvent(eventId, type as "external" | "internal")
          .then((response) => {
            setProposalType(type);
            // Normalize financialPlan for external so fieldRepeater can use it
            const data = response.data.data || {};
            let financialPlan: any = {};
            try {
              if (data.financialPlan) {
                const parsed =
                  typeof data.financialPlan === "string"
                    ? JSON.parse(data.financialPlan)
                    : data.financialPlan;
                if (Array.isArray(parsed)) {
                  financialPlan = parsed.reduce((acc: any, row: any, idx: number) => {
                    acc[idx] = row;
                    return acc;
                  }, {});
                } else if (parsed && typeof parsed === "object") {
                  financialPlan = parsed;
                } else {
                  financialPlan = { 0: { item: String(parsed) } };
                }
              }
            } catch {
              financialPlan = { 0: { item: String(data.financialPlan || "") } };
            }
            // Parse evaluationMechanicsPlan first to ensure proper structure
            const parsedEvaluationMechanicsPlan = (() => {
              const rawData = response.data.data?.evaluationMechanicsPlan;
              if (!rawData) {
                return {
                  objectivesImpact: {},
                  objectivesOutcome: {},
                  objectivesOutput: {},
                  objectivesActivities: {},
                  objectivesInput: {},
                  objectivesImpactLabel: "Impact",
                  objectivesOutcomeLabel: "Outcome",
                  objectivesOutputLabel: "Output",
                  objectivesActivitiesLabel: "Activities",
                  objectivesInputLabel: "Input",
                };
              }
              try {
                const parsed = typeof rawData === 'string' ? JSON.parse(rawData) : rawData;
                // Ensure nested structure exists - preserve all existing data, add defaults only if missing
                // Use spread to create new objects to ensure reactivity
                return {
                  objectivesImpact: parsed.objectivesImpact ? { ...parsed.objectivesImpact } : {},
                  objectivesOutcome: parsed.objectivesOutcome ? { ...parsed.objectivesOutcome } : {},
                  objectivesOutput: parsed.objectivesOutput ? { ...parsed.objectivesOutput } : {},
                  objectivesActivities: parsed.objectivesActivities ? { ...parsed.objectivesActivities } : {},
                  objectivesInput: parsed.objectivesInput ? { ...parsed.objectivesInput } : {},
                  objectivesImpactLabel: parsed.objectivesImpactLabel || "Impact",
                  objectivesOutcomeLabel: parsed.objectivesOutcomeLabel || "Outcome",
                  objectivesOutputLabel: parsed.objectivesOutputLabel || "Output",
                  objectivesActivitiesLabel: parsed.objectivesActivitiesLabel || "Activities",
                  objectivesInputLabel: parsed.objectivesInputLabel || "Input",
                };
              } catch (e) {
                console.error('Error parsing evaluationMechanicsPlan:', e);
                return {
                  objectivesImpact: {},
                  objectivesOutcome: {},
                  objectivesOutput: {},
                  objectivesActivities: {},
                  objectivesInput: {},
                  objectivesImpactLabel: "Impact",
                  objectivesOutcomeLabel: "Outcome",
                  objectivesOutputLabel: "Output",
                  objectivesActivitiesLabel: "Activities",
                  objectivesInputLabel: "Input",
                };
              }
            })();

            setFormData({
              ...response.data.data,
              sdg: response.data.data?.sdg
                ? JSON.parse(response.data.data.sdg)
                : {},
              extensionServiceType: response.data.data?.extensionServiceType
                ? JSON.parse(response.data.data.extensionServiceType)
                : {},
              externalServiceType: response.data.data?.externalServiceType
                ? JSON.parse(response.data.data.externalServiceType)
                : {},
              eventProposalType: response.data.data?.eventProposalType
                ? JSON.parse(response.data.data.eventProposalType)
                : {},
              workPlan: response.data.data?.workPlan
                ? (typeof response.data.data.workPlan === 'string' 
                    ? JSON.parse(response.data.data.workPlan) 
                    : response.data.data.workPlan)
                : {},
              financialPlan,
              financialRequirement: response.data.data?.financialRequirement
                ? (typeof response.data.data.financialRequirement === 'string'
                    ? JSON.parse(response.data.data.financialRequirement)
                    : response.data.data.financialRequirement)
                : {},
              evaluationMechanicsPlan: parsedEvaluationMechanicsPlan,
            });
          })
          .catch(() => {
            showSnackbarMessage(
              "An error occured in retrieving event details",
              "error"
            );
          });
      }
    }
  }, [eventType]);

  useEffect(() => {
    setProposalType("");
    setFieldErrors([]);
    setShowOtherSourceOfFund(false);
    if (open === false) {
      onClose && onClose();
    }
  }, [open]);

  const submitCallback = useCallback(async () => {
    setDisableButton(true);
    let response;
    try {
      // Stringify object fields for backend compatibility
      const processedFormData = { ...formData };
      if (proposalType === "internal") {
        if (processedFormData.workPlan && typeof processedFormData.workPlan === 'object') {
          processedFormData.workPlan = JSON.stringify(processedFormData.workPlan);
        }
        if (processedFormData.financialRequirement && typeof processedFormData.financialRequirement === 'object') {
          processedFormData.financialRequirement = JSON.stringify(processedFormData.financialRequirement);
        }
        if (processedFormData.evaluationMechanicsPlan && typeof processedFormData.evaluationMechanicsPlan === 'object') {
          processedFormData.evaluationMechanicsPlan = JSON.stringify(processedFormData.evaluationMechanicsPlan);
        }
        // Remove workPlan_columns if it exists (not expected by backend)
        if ('workPlan_columns' in processedFormData) {
          delete processedFormData.workPlan_columns;
        }
      }
      
      if (proposalType === "external") {
        const payload: any = { ...processedFormData };
        if (payload.financialPlan && typeof payload.financialPlan === 'object') {
          payload.financialPlan = JSON.stringify(payload.financialPlan);
        }
        // Stringify evaluationMechanicsPlan for external events (includes objective labels)
        if (payload.evaluationMechanicsPlan && typeof payload.evaluationMechanicsPlan === 'object') {
          payload.evaluationMechanicsPlan = JSON.stringify(payload.evaluationMechanicsPlan);
        }
        response = await createExternalEvent(payload);
      }
      if (proposalType === "internal")
        response = await createInternalEvent(processedFormData);

      if (response) {
        showSnackbarMessage("Successfully created proposal!", "success");
        setOpen(false);
        setFormData({});
      }
    } catch (err: any) {
      if (err.response?.data) {
        const message = err.response.data.message || err.response.data.error || "Unknown error";
        const errors = err.response.data.fieldError ?? [];

        setFieldErrors(errors);
        showSnackbarMessage(`Error occurred: ${message}`, "error");
      } else {
        const errorMessage = err?.message || err?.toString() || "Unknown error occurred";
        showSnackbarMessage(`Error occurred: ${errorMessage}`, "error");
      }
    } finally {
      setDisableButton(false);
      onSubmit && onSubmit();
    }
  }, [proposalType, formData]);

  const DefaultForm: (FormGenTemplateProps | FormGenTemplateProps[])[] = [
    {
      hidden: proposalType !== "",
      type: "label",
      message: "Select an event type first",
    },
    [
      {
        flex: 1,
        hidden: proposalType !== "",
        type: "component",
        component: (
          <PrimaryButton
            sx={{ 
              flex: 1, 
              backgroundColor: "#7c5f0b",
              width: "100%",
              minHeight: "60px",
              fontSize: "1rem",
              fontWeight: "600"
            }}
            label="External event"
            fullWidth
            onClick={() => {
              setProposalType("external");
              // setForceRefresh(forceRefresh + 1);
              setFormData({
                evaluationMechanicsPlan: {
                  objectivesImpact: {},
                  objectivesOutcome: {},
                  objectivesOutput: {},
                  objectivesActivities: {},
                  objectivesInput: {},
                  objectivesImpactLabel: "Impact",
                  objectivesOutcomeLabel: "Outcome",
                  objectivesOutputLabel: "Output",
                  objectivesActivitiesLabel: "Activities",
                  objectivesInputLabel: "Input",
                },
              });
            }}
          />
        ),
      },
      {
        flex: 1,
        hidden: proposalType !== "",
        type: "component",
        component: (
          <PrimaryButton
            sx={{ 
              flex: 1, 
              backgroundColor: "#0e3e6c",
              width: "100%",
              minHeight: "60px",
              fontSize: "1rem",
              fontWeight: "600"
            }}
            label="Internal event"
            fullWidth
            onClick={() => {
              setProposalType("internal");
              // setForceRefresh(forceRefresh + 1);
              setFormData({
                evaluationMechanicsPlan: {},
                financialRequirement: {},
                workPlan: {},
              });
            }}
          />
        ),
      },
    ],
  ];

  const InternalForm: (FormGenTemplateProps | FormGenTemplateProps[])[] = [
    [{ id: "title", type: "text", message: "Event Title", required: true }],
    [
      {
        id: "evaluationSendTime",
        required: true,
        type: "datetime",
        message: "Datetime to send evaluation email",
      },
    ],
    [
      {
        flex: 1,
        id: "durationStart",
        required: true,
        type: "datetime",
        message: "Event Start Date",
      },
      {
        flex: 1,
        id: "durationEnd",
        required: true,
        type: "datetime",
        message: "Event End Date",
      },
    ],
    [
      { flex: 1, id: "venue", type: "text", message: "Venue", required: true },
      {
        flex: 1,
        id: "modeOfDelivery",
        required: true,
        type: "dropdown",
        message: "Mode of Delivery",
        menu: [
          { key: "Online", value: "Online" },
          { key: "Face-To-Face", value: "Face-To-Face" },
        ],
      },
    ],
    [
      {
        id: "partner",
        type: "text",
        required: true,
        message: "Partner Office/College/Department",
      },
    ],
    [
      {
        id: "participant",
        type: "text",
        required: true,
        message: "Type of Participant",
      },
    ],
    [
      {
        id: "maleTotal",
        type: "number",
        required: true,
        message: "Total Male",
        onUse: (event) => {
          // Enforce max 2 digits (0-99) and digits only
          const raw = String(event?.target?.value ?? "");
          const digitsOnly = raw.replace(/\D+/g, "").slice(0, 2);
          immutableSetFormData({ maleTotal: digitsOnly });
        },
      },
      {
        id: "femaleTotal",
        type: "number",
        required: true,
        message: "Total Female",
        onUse: (event) => {
          // Enforce max 2 digits (0-99) and digits only
          const raw = String(event?.target?.value ?? "");
          const digitsOnly = raw.replace(/\D+/g, "").slice(0, 2);
          immutableSetFormData({ femaleTotal: digitsOnly });
        },
      },
    ],
    [
      {
        id: "eventProposalType",
        required: true,
        type: "checkbox",
        message: "Event Proposal Type",
        selectionQuestion: [
          {
            initialValue: false,
            label: "Project",
          },
          {
            initialValue: false,
            label: "Program",
          },
          {
            initialValue: false,
            label: "Activity",
          },
        ],
      },
    ],
    {
      id: "projectTeam",
      type: "textQuestion",
      required: true,
      message: "Project Team",
    },
    {
      id: "rationale",
      required: true,
      type: "textQuestion",
      message: "Rationale/Background",
    },
    {
      id: "objectives",
      required: true,
      type: "textQuestion",
      message: "Objective",
    },
    {
      id: "description",
      required: true,
      type: "textQuestion",
      message: "Description, Strategies and Methods (Activities / Schedule)",
    },
    {
      id: "sustainabilityPlan",
      required: true,
      type: "textQuestion",
      message: "Sustainability Plan",
    },
    { type: "section", message: "Work Plan (Gantt Chart)" },
    {
      type: "ganttTable",
      fieldKey: "workPlan",
      message: "Work Plan Timeline",
      initialColumns: ['Activities', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'],
    },
    { type: "section", message: "Financial Requirements and Source of Funds" },
    [
      {
        type: "label",
        message:
          "Click the button below to add rows for financial requirements",
      },
    ],
    {
      fieldKey: "financialRequirement",
      type: "fieldRepeater",
      field: [
        [{ id: "item", type: "text", message: "Item Description", required: true }],
        [
          { id: "qty", type: "number", message: "Quantity" },
          { id: "unit", type: "text", message: "Unit" },
          { id: "unitCost", type: "number", message: "Unit Cost" },
          { id: "total", type: "number", message: "Total" },
        ],
      ],
    },
    { type: "section", message: "Monitoring and Evaluation Mechanics / Plan" },
    [
      {
        type: "label",
        message: "Click the button below to add rows for Monitoring Plan",
      },
    ],
    {
      fieldKey: "evaluationMechanicsPlan",
      type: "fieldRepeater",
      field: [
        [
          { id: "specificObjective", type: "text", message: "Objectives" },
          {
            id: "performanceIndicator",
            type: "text",
            message: "Performance Indicators",
          },
        ],
        [
          { id: "baselineData", type: "text", message: "Baseline Data" },
          {
            id: "performanceTarget",
            type: "text",
            message: "Performance Target",
          },
          { id: "dataSource", type: "text", message: "Data Source" },
        ],
        [
          {
            id: "collectionMethod",
            type: "text",
            message: "Collection Method",
          },
          {
            id: "frequencyOfCollection",
            type: "text",
            message: "Frequency of data collection",
          },
          {
            id: "personResponsible",
            type: "text",
            message: "Office/Person Responsible",
          },
        ],
      ],
    },
  ];

  const ExternalForm: (FormGenTemplateProps | FormGenTemplateProps[])[] = [
    [
      {
        id: "title",
        required: true,
        type: "text",
        message: "Title",
      },
    ],
    [
      {
        id: "location",
        required: true,
        type: "text",
        message: "Location",
      },
    ],
    [
      {
        id: "evaluationSendTime",
        required: true,
        type: "datetime",
        message: "Datetime to send evaluation email",
      },
    ],
    [
      {
        id: "durationStart",
        required: true,
        type: "datetime",
        message: "Duration (Start Date time)",
      },
      {
        id: "durationEnd",
        required: true,
        type: "datetime",
        message: "Duration (End Date time)",
      },
    ],
    [
      {
        id: "externalServiceType",
        required: true,
        type: "checkbox",
        message: "External Service Type",
        selectionQuestion: [
          {
            initialValue: false,
            label:
              "Extension Service Program/Project/Activity is requested by clients.",
          },
          {
            initialValue: false,
            label:
              "Extension Service Program/Project/Activity is Department's initiative.",
          },
        ],
      },
    ],
    [
      {
        id: "eventProposalType",
        required: true,
        type: "checkbox",
        message: "Event Proposal Type",
        selectionQuestion: [
          {
            initialValue: false,
            label: "Project",
          },
          {
            initialValue: false,
            label: "Program",
          },
          {
            initialValue: false,
            label: "Activity",
          },
        ],
      },
    ],
    [
      {
        id: "extensionServiceType",
        type: "checkbox",
        required: true,
        message: "Type of Extension Service Agenda (Choose only one)",
        selectionQuestion: [
          {
            initialValue: false,
            label:
              "BatStateU Inclusive Social Innovation for Regional Growth (BISIG) Program",
          },
          {
            initialValue: false,
            label:
              "Livelihood and other Entrepreneurship related on Agri-Fisheries (LEAF)",
          },
          {
            initialValue: false,
            label:
              "Environment and Natural Resources Conservation, Protection, and Rehabilitation Program",
          },
          {
            initialValue: false,
            label: "SMART Analytics and Engineering Innovation",
          },
          {
            initialValue: false,
            label:
              "Adopt-a-Municipality/Barangay/School/Social Development Thru BIDANI Implementation",
          },
          {
            initialValue: false,
            label: "Community Outreach",
          },
          {
            initialValue: false,
            label: "Technical-Vocational Education and Training (TVET) Program",
          },
          {
            initialValue: false,
            label: "Technology Transfer and Adoption/Utilization Program",
          },
          {
            initialValue: false,
            label: "Technical Assistance and Advisory Services Program",
          },
          {
            initialValue: false,
            label: "Parents’ Empowerment through Social Development (PESODEV)",
          },
          {
            initialValue: false,
            label: "Gender and Development",
          },
          {
            initialValue: false,
            label:
              "Disaster Risk Reduction and Management and Disaster Preparedness and Response/Climate Change Adaptation (DRRM and DPR/CCA)",
          },
        ],
      },
    ],
    [
      {
        id: "sdg",
        type: "checkbox",
        required: true,
        message: "Sustainable Development Goals (SDG)",
        selectionQuestion: [
          {
            initialValue: false,
            label: "No Poverty",
          },
          {
            initialValue: false,
            label: "Zero Hunger",
          },
          {
            label: "Good Health and Well-Being",
            initialValue: false,
          },
          { label: "Quality Education", initialValue: false },
          { label: "Gender Equality", initialValue: false },
          {
            label: "Clean Water and Sanitation",
            initialValue: false,
          },
          {
            label: "Affordable and Clean Energy",
            initialValue: false,
          },
          {
            label: "Decent Work and Economic Growth",
            initialValue: false,
          },
          {
            label: "Industry, Innovation and Infrastructure",
            initialValue: false,
          },
          { label: "Reduced Inequalities", initialValue: false },
          {
            label: "Sustainable Cities and Communities",
            initialValue: false,
          },
          {
            label: "Responsible Consumption and Production",
            initialValue: false,
          },
          { label: "Climate Action", initialValue: false },
          { label: "Life Below Water", initialValue: false },
          { label: "Life on Land", initialValue: false },
          {
            label: "Peace, Justice and Strong Institutions",
            initialValue: false,
          },
          {
            label: "Partnerships for the Goals",
            initialValue: false,
          },
        ],
      },
    ],
    [
      {
        id: "sourceOfFund",
        type: "dropdown",
        required: true,
        message: "Source of fund",
        menu: [
          { key: "STF", value: "STF" },
          { key: "MDS", value: "MDS" },
          { key: "Others...", value: "Others" },
        ],
        hidden: showOtherSourceOfFund,
        onUse: (event) => {
          if (event.target.value === "Others") {
            setShowOtherSourceOfFund(true);
          }
        },
      },
      {
        id: "sourceOfFund",
        type: "text",
        required: true,
        message: "Source of fund",
        hidden: !showOtherSourceOfFund,
        endIcon: (
          <IconButton
            onClick={() => {
              setShowOtherSourceOfFund(false);
            }}
          >
            <CloseIcon />
          </IconButton>
        ),
      },
      {
        id: "totalCost",
        required: true,
        type: "number",
        message: "Total Cost",
      },
    ],
    {
      id: "orgInvolved",
      required: true,
      type: "textQuestion",
      message: "Office/s / College/s / Organization/s Involved",
    },
    {
      id: "programInvolved",
      required: true,
      type: "textQuestion",
      message:
        "Program/s Involved (specify the programs under the college implementing the project)",
    },
    {
      id: "projectLeader",
      required: true,
      type: "textQuestion",
      message: "Project Leader, Assistant Project Leader and Coordinators:",
    },
    {
      id: "partners",
      required: true,
      type: "textQuestion",
      message: "Partner Agencies",
    },
    {
      id: "beneficiaries",
      required: true,
      type: "textQuestion",
      message: "Beneficiaries (Type and Number of Male and Female)",
    },
    {
      id: "rationale",
      required: true,
      type: "textQuestion",
      message: "Rationale (brief description of the situation)",
    },
    {
      id: "objectives",
      required: true,
      type: "textQuestion",
      message: "Objectives (General and Specific)",
    },
    {
      id: "expectedOutput",
      required: true,
      type: "textQuestion",
      message: "Program/Project Expected Output",
    },
    {
      id: "description",
      required: true,
      type: "textQuestion",
      message: "Description, Strategies and Methods (Activities / Schedule)",
    },
    {
      type: "section",
      message: "Financial Plan (Financial Requirements and Source of Funds)",
    },
    [
      {
        type: "label",
        message: "Click the button below to add rows for financial requirements",
      },
    ],
    {
      fieldKey: "financialPlan",
      type: "fieldRepeater",
      field: [
        [{ id: "item", type: "text", message: "Item Description", required: true }],
        [
          { id: "qty", type: "number", message: "Quantity" },
          { id: "unit", type: "text", message: "Unit" },
          { id: "unitCost", type: "number", message: "Unit Cost" },
          { id: "total", type: "number", message: "Total" },
        ],
      ],
    },
    {
      id: "dutiesOfPartner",
      required: true,
      type: "textQuestion",
      message:
        "Functional Relationships with the Partner Agencies (Duties / Tasks of the Partner Agencies)",
    },
    {
      id: "sustainabilityPlan",
      required: true,
      type: "textQuestion",
      message: "Sustainability Plan",
    },
    {
      type: "section",
      message: "Monitoring and Evaluation Mechanics / Plan",
    },
    [
      {
        type: "text",
        message: "Objectives",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesImpactLabel) ||
          "Impact",
        onUse: (event) => {
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...(formData.evaluationMechanicsPlan || {}),
              objectivesImpactLabel: event.target.value,
            },
          });
        },
      },
    ],
    [
      {
        type: "text",
        message: "Performance Indicators",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesImpact &&
            formData.evaluationMechanicsPlan.objectivesImpact.performanceIndicator) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesImpact: {
                ...formData.evaluationMechanicsPlan.objectivesImpact,
                performanceIndicator: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Baseline Data",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesImpact &&
            formData.evaluationMechanicsPlan.objectivesImpact.baselineData) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesImpact: {
                ...formData.evaluationMechanicsPlan.objectivesImpact,
                baselineData: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Performance Target",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesImpact &&
            formData.evaluationMechanicsPlan.objectivesImpact.performanceTarget) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesImpact: {
                ...formData.evaluationMechanicsPlan.objectivesImpact,
                performanceTarget: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Data source",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesImpact &&
            formData.evaluationMechanicsPlan.objectivesImpact.dataSource) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesImpact: {
                ...formData.evaluationMechanicsPlan.objectivesImpact,
                dataSource: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Collection method",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesImpact &&
            formData.evaluationMechanicsPlan.objectivesImpact.collectionMethod) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesImpact: {
                ...formData.evaluationMechanicsPlan.objectivesImpact,
                collectionMethod: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Frequency of Data Collection",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesImpact &&
            formData.evaluationMechanicsPlan.objectivesImpact
              .frequencyOfDataCollection) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesImpact: {
                ...formData.evaluationMechanicsPlan.objectivesImpact,
                frequencyOfDataCollection: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Office/Persons Responsible",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesImpact &&
            formData.evaluationMechanicsPlan.objectivesImpact.officeResponsible) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesImpact: {
                ...formData.evaluationMechanicsPlan.objectivesImpact,
                officeResponsible: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Objectives",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutcomeLabel) ||
          "Outcome",
        onUse: (event) => {
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...(formData.evaluationMechanicsPlan || {}),
              objectivesOutcomeLabel: event.target.value,
            },
          });
        },
      },
    ],
    [
      {
        type: "text",
        message: "Performance Indicators",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutcome &&
            formData.evaluationMechanicsPlan.objectivesOutcome
              .performanceIndicator) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutcome: {
                ...formData.evaluationMechanicsPlan.objectivesOutcome,
                performanceIndicator: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Baseline Data",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutcome &&
            formData.evaluationMechanicsPlan.objectivesOutcome.baselineData) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutcome: {
                ...formData.evaluationMechanicsPlan.objectivesOutcome,
                baselineData: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Performance Target",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutcome &&
            formData.evaluationMechanicsPlan.objectivesOutcome
              .performanceTarget) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutcome: {
                ...formData.evaluationMechanicsPlan.objectivesOutcome,
                performanceTarget: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Data source",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutcome &&
            formData.evaluationMechanicsPlan.objectivesOutcome.dataSource) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutcome: {
                ...formData.evaluationMechanicsPlan.objectivesOutcome,
                dataSource: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Collection method",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutcome &&
            formData.evaluationMechanicsPlan.objectivesOutcome.collectionMethod) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutcome: {
                ...formData.evaluationMechanicsPlan.objectivesOutcome,
                collectionMethod: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Frequency of Data Collection",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutcome &&
            formData.evaluationMechanicsPlan.objectivesOutcome
              .frequencyOfDataCollection) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutcome: {
                ...formData.evaluationMechanicsPlan.objectivesOutcome,
                frequencyOfDataCollection: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Office/Persons Responsible",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutcome &&
            formData.evaluationMechanicsPlan.objectivesOutcome
              .officeResponsible) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutcome: {
                ...formData.evaluationMechanicsPlan.objectivesOutcome,
                officeResponsible: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Objectives",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutputLabel) ||
          "Output",
        onUse: (event) => {
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...(formData.evaluationMechanicsPlan || {}),
              objectivesOutputLabel: event.target.value,
            },
          });
        },
      },
    ],
    [
      {
        type: "text",
        message: "Performance Indicators",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutput &&
            formData.evaluationMechanicsPlan.objectivesOutput
              .performanceIndicator) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutput: {
                ...formData.evaluationMechanicsPlan.objectivesOutput,
                performanceIndicator: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Baseline Data",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutput &&
            formData.evaluationMechanicsPlan.objectivesOutput.baselineData) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutput: {
                ...formData.evaluationMechanicsPlan.objectivesOutput,
                baselineData: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Performance Target",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutput &&
            formData.evaluationMechanicsPlan.objectivesOutput
              .performanceTarget) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutput: {
                ...formData.evaluationMechanicsPlan.objectivesOutput,
                performanceTarget: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Data source",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutput &&
            formData.evaluationMechanicsPlan.objectivesOutput.dataSource) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutput: {
                ...formData.evaluationMechanicsPlan.objectivesOutput,
                dataSource: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Collection method",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutput &&
            formData.evaluationMechanicsPlan.objectivesOutput
              .collectionMethod) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutput: {
                ...formData.evaluationMechanicsPlan.objectivesOutput,
                collectionMethod: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Frequency of Data Collection",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutput &&
            formData.evaluationMechanicsPlan.objectivesOutput
              .frequencyOfDataCollection) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutput: {
                ...formData.evaluationMechanicsPlan.objectivesOutput,
                frequencyOfDataCollection: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Office/Persons Responsible",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesOutput &&
            formData.evaluationMechanicsPlan.objectivesOutput
              .officeResponsible) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesOutput: {
                ...formData.evaluationMechanicsPlan.objectivesOutput,
                officeResponsible: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Objectives",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesActivitiesLabel) ||
          "Activities",
        onUse: (event) => {
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...(formData.evaluationMechanicsPlan || {}),
              objectivesActivitiesLabel: event.target.value,
            },
          });
        },
      },
    ],
    [
      {
        type: "text",
        message: "Performance Indicators",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesActivities &&
            formData.evaluationMechanicsPlan.objectivesActivities
              .performanceIndicator) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesActivities: {
                ...formData.evaluationMechanicsPlan.objectivesActivities,
                performanceIndicator: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Baseline Data",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesActivities &&
            formData.evaluationMechanicsPlan.objectivesActivities.baselineData) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesActivities: {
                ...formData.evaluationMechanicsPlan.objectivesActivities,
                baselineData: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Performance Target",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesActivities &&
            formData.evaluationMechanicsPlan.objectivesActivities
              .performanceTarget) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesActivities: {
                ...formData.evaluationMechanicsPlan.objectivesActivities,
                performanceTarget: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Data source",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesActivities &&
            formData.evaluationMechanicsPlan.objectivesActivities.dataSource) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesActivities: {
                ...formData.evaluationMechanicsPlan.objectivesActivities,
                dataSource: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Collection method",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesActivities &&
            formData.evaluationMechanicsPlan.objectivesActivities.collectionMethod) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesActivities: {
                ...formData.evaluationMechanicsPlan.objectivesActivities,
                collectionMethod: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Frequency of Data Collection",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesActivities &&
            formData.evaluationMechanicsPlan.objectivesActivities
              .frequencyOfDataCollection) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesActivities: {
                ...formData.evaluationMechanicsPlan.objectivesActivities,
                frequencyOfDataCollection: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Office/Persons Responsible",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesActivities &&
            formData.evaluationMechanicsPlan.objectivesActivities
              .officeResponsible) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesActivities: {
                ...formData.evaluationMechanicsPlan.objectivesActivities,
                officeResponsible: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Objectives",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesInputLabel) ||
          "Input",
        onUse: (event) => {
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...(formData.evaluationMechanicsPlan || {}),
              objectivesInputLabel: event.target.value,
            },
          });
        },
      },
    ],
    [
      {
        type: "text",
        message: "Performance Indicators",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesInput &&
            formData.evaluationMechanicsPlan.objectivesInput.performanceIndicator) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesInput: {
                ...formData.evaluationMechanicsPlan.objectivesInput,
                performanceIndicator: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Baseline Data",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesInput &&
            formData.evaluationMechanicsPlan.objectivesInput.baselineData) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesInput: {
                ...formData.evaluationMechanicsPlan.objectivesInput,
                baselineData: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Performance Target",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesInput &&
            formData.evaluationMechanicsPlan.objectivesInput.performanceTarget) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesInput: {
                ...formData.evaluationMechanicsPlan.objectivesInput,
                performanceTarget: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Data source",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesInput &&
            formData.evaluationMechanicsPlan.objectivesInput.dataSource) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesInput: {
                ...formData.evaluationMechanicsPlan.objectivesInput,
                dataSource: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Collection method",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesInput &&
            formData.evaluationMechanicsPlan.objectivesInput.collectionMethod) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesInput: {
                ...formData.evaluationMechanicsPlan.objectivesInput,
                collectionMethod: event.target.value,
              },
            },
          }),
      },
      {
        type: "text",
        message: "Frequency of Data Collection",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesInput &&
            formData.evaluationMechanicsPlan.objectivesInput
              .frequencyOfDataCollection) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesInput: {
                ...formData.evaluationMechanicsPlan.objectivesInput,
                frequencyOfDataCollection: event.target.value,
              },
            },
          }),
      },
    ],
    [
      {
        type: "text",
        message: "Office/Persons Responsible",
        value:
          (formData?.evaluationMechanicsPlan &&
            formData.evaluationMechanicsPlan.objectivesInput &&
            formData.evaluationMechanicsPlan.objectivesInput.officeResponsible) ||
          "",
        onUse: (event) =>
          immutableSetFormData({
            evaluationMechanicsPlan: {
              ...formData.evaluationMechanicsPlan,
              objectivesInput: {
                ...formData.evaluationMechanicsPlan.objectivesInput,
                officeResponsible: event.target.value,
              },
            },
          }),
      },
    ],
  ];

  return (
    <>
      <PopupModal
        header={`Event Proposal Form ${
          proposalType !== "" ? "(" + proposalType + ")" : ""
        }`}
        subHeader="Submit your proposal by filling up the form details"
        open={open}
        setOpen={setOpen}
        maxWidth="90vw"
        zval={zval}
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
            {proposalType === "external" && (
              <FormGeneratorTemplate
                key={`external-${formData?.evaluationMechanicsPlan?.objectivesImpactLabel || ""}-${formData?.evaluationMechanicsPlan?.objectivesOutcomeLabel || ""}-${formData?.evaluationMechanicsPlan?.objectivesOutputLabel || ""}-${formData?.evaluationMechanicsPlan?.objectivesActivitiesLabel || ""}-${formData?.evaluationMechanicsPlan?.objectivesInputLabel || ""}`}
                viewOnly={viewOnly}
                enableAutoFieldCheck={true}
                fieldErrors={fieldErrors}
                template={ExternalForm}
              />
            )}
            {proposalType === "internal" && (
              <FormGeneratorTemplate
                dataLoader
                viewOnly={viewOnly}
                enableAutoFieldCheck={true}
                template={InternalForm}
                fieldErrors={fieldErrors}
              />
            )}
            {proposalType === "" && (
              <FormGeneratorTemplate
                enableAutoFieldCheck={true}
                template={DefaultForm}
                fieldErrors={[]}
              />
            )}
          </FlexBox>
        </form>
        <FlexBox justifyContent="flex-end" marginTop="10px" gap="10px" alignItems="center">
          <FlexBox gap="10px">
            {componentsBeforeSubmit}
            {!hideSubmit && proposalType !== "" && (
              <PrimaryButton
                label="Submit"
                size="small"
                icon={<SendIcon />}
                disabled={disableButton}
                onClick={() => {
                  submitCallback();
                }}
              />
            )}
          </FlexBox>
        </FlexBox>
      </PopupModal>
    </>
  );
};

export default EventProposalForm;

