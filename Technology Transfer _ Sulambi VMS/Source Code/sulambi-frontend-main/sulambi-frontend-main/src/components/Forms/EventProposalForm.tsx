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
import { looseJsonParse, toJsonString } from "../../utils/looseJson";

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

/** One empty row for Monitoring and Evaluation (1 objective by default; officer adds more via Add Field) */
const EMPTY_M_E_ROW = {
  specificObjective: "",
  performanceIndicator: "",
  baselineData: "",
  performanceTarget: "",
  dataSource: "",
  collectionMethod: "",
  frequencyOfCollection: "",
  personResponsible: "",
};

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
            const parseObj = <T,>(val: unknown, fallback: T): T =>
              looseJsonParse<T>(val, fallback);
            const parseCheckboxList = (val: unknown): string[] => {
              const parsed = parseObj<any>(val, []);
              if (Array.isArray(parsed)) return parsed.filter((x) => typeof x === "string");
              if (parsed && typeof parsed === "object") {
                // Support legacy object shape: { "Label": true, ... }
                return Object.keys(parsed).filter((k) => Boolean((parsed as any)[k]));
              }
              return [];
            };

            let financialPlan: any = {};
            try {
              if (data.financialPlan) {
                const parsed = parseObj<any>(data.financialPlan, {});
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
            // Parse evaluationMechanicsPlan: use repeater shape { "0": {...}, "1": {...} } for both internal and external.
            // If saved data is old external format (objectivesImpact, objectivesOutcome, etc.), convert to repeater shape.
            const parsedEvaluationMechanicsPlan = (() => {
              const rawData = response.data.data?.evaluationMechanicsPlan;
              if (!rawData) return { "0": { ...EMPTY_M_E_ROW } };
              try {
                const parsed = parseObj<any>(rawData, {});
                if (!parsed || typeof parsed !== 'object') return { "0": { ...EMPTY_M_E_ROW } };
                if (Array.isArray(parsed)) {
                  const rows: Record<string, any> = {};
                  parsed.forEach((row, idx) => {
                    rows[String(idx)] = row;
                  });
                  return Object.keys(rows).length > 0 ? rows : { "0": { ...EMPTY_M_E_ROW } };
                }
                const hasOldExternalShape =
                  'objectivesImpact' in parsed ||
                  'objectivesOutcome' in parsed ||
                  'objectivesOutput' in parsed;
                if (!hasOldExternalShape) return parsed;
                const toRow = (label: string, obj: any) => ({
                  specificObjective: label,
                  performanceIndicator: obj?.performanceIndicator ?? '',
                  baselineData: obj?.baselineData ?? '',
                  performanceTarget: obj?.performanceTarget ?? '',
                  dataSource: obj?.dataSource ?? '',
                  collectionMethod: obj?.collectionMethod ?? '',
                  frequencyOfCollection: obj?.frequencyOfDataCollection ?? '',
                  personResponsible: obj?.officeResponsible ?? '',
                });
                const rows: Record<string, any> = {};
                let idx = 0;
                if (parsed.objectivesImpactLabel != null || parsed.objectivesImpact) {
                  rows[String(idx++)] = toRow(parsed.objectivesImpactLabel || 'Impact', parsed.objectivesImpact);
                }
                if (parsed.objectivesOutcomeLabel != null || parsed.objectivesOutcome) {
                  rows[String(idx++)] = toRow(parsed.objectivesOutcomeLabel || 'Outcome', parsed.objectivesOutcome);
                }
                if (parsed.objectivesOutputLabel != null || parsed.objectivesOutput) {
                  rows[String(idx++)] = toRow(parsed.objectivesOutputLabel || 'Output', parsed.objectivesOutput);
                }
                if (parsed.objectivesActivitiesLabel != null || parsed.objectivesActivities) {
                  rows[String(idx++)] = toRow(parsed.objectivesActivitiesLabel || 'Activities', parsed.objectivesActivities);
                }
                if (parsed.objectivesInputLabel != null || parsed.objectivesInput) {
                  rows[String(idx++)] = toRow(parsed.objectivesInputLabel || 'Input', parsed.objectivesInput);
                }
                return Object.keys(rows).length > 0 ? rows : { "0": { ...EMPTY_M_E_ROW } };
              } catch (e) {
                console.error('Error parsing evaluationMechanicsPlan:', e);
                return { "0": { ...EMPTY_M_E_ROW } };
              }
            })();

            setFormData({
              ...response.data.data,
              // These fields may be stored as JSON OR Python-style repr (single quotes).
              // Parse best-effort; never throw and block editing.
              sdg: response.data.data?.sdg ? parseCheckboxList(response.data.data.sdg) : [],
              extensionServiceType: response.data.data?.extensionServiceType
                ? parseCheckboxList(response.data.data.extensionServiceType)
                : [],
              externalServiceType: response.data.data?.externalServiceType
                ? parseCheckboxList(response.data.data.externalServiceType)
                : [],
              eventProposalType: response.data.data?.eventProposalType
                ? parseCheckboxList(response.data.data.eventProposalType)
                : [],
              // Keep workPlan as-is (string/object). EditableGanttTable will hydrate it lazily.
              workPlan: response.data.data?.workPlan ?? {},
              financialPlan,
              financialRequirement: response.data.data?.financialRequirement
                ? parseObj<any>(response.data.data.financialRequirement, {})
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
      // Small delay to allow any pending debounced updates (like Gantt chart) to complete
      // This ensures workPlan and other debounced fields are saved before submission
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Stringify object fields for backend compatibility
      // Note: formData is in the dependency array, so it should be up-to-date after the delay
      const processedFormData = { ...formData };
      if (proposalType === "internal") {
        // Ensure checkbox/selection objects are persisted as JSON strings (not "[object Object]" or Python-style repr)
        if (processedFormData.eventProposalType && typeof processedFormData.eventProposalType === "object") {
          processedFormData.eventProposalType = toJsonString(processedFormData.eventProposalType, "[]");
        }
        // Always ensure workPlan is included and properly stringified
        // Handle both object and string cases, and ensure it's never undefined
        if (processedFormData.workPlan) {
          if (typeof processedFormData.workPlan === 'object') {
            processedFormData.workPlan = JSON.stringify(processedFormData.workPlan);
          } else if (typeof processedFormData.workPlan === 'string') {
            // Already a string, use as-is
          } else {
            // Fallback to empty object if invalid type
            processedFormData.workPlan = "{}";
          }
        } else {
          // If workPlan is missing, set to empty object string
          processedFormData.workPlan = "{}";
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
        // Persist these as JSON strings so edits can reliably JSON.parse them later.
        if (payload.sdg && typeof payload.sdg === "object") payload.sdg = toJsonString(payload.sdg, "[]");
        if (payload.extensionServiceType && typeof payload.extensionServiceType === "object") {
          payload.extensionServiceType = toJsonString(payload.extensionServiceType, "[]");
        }
        if (payload.externalServiceType && typeof payload.externalServiceType === "object") {
          payload.externalServiceType = toJsonString(payload.externalServiceType, "[]");
        }
        if (payload.eventProposalType && typeof payload.eventProposalType === "object") {
          payload.eventProposalType = toJsonString(payload.eventProposalType, "[]");
        }
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
              setFormData({
                evaluationMechanicsPlan: { "0": { ...EMPTY_M_E_ROW } },
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
              setFormData({
                evaluationMechanicsPlan: { "0": { ...EMPTY_M_E_ROW } },
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
        id: "beneficiaryEvaluationPin",
        type: "text",
        required: true,
        message: "Beneficiary evaluation PIN (required). Exactly 5 digits. All beneficiaries use this PIN to submit feedback for this event.",
        placeholder: "5 digits",
        inputProps: { maxLength: 5, inputMode: "numeric" as const },
        onUse: (e: { target: { value: string } }) => {
          const v = (e.target.value || "").replace(/\D/g, "").slice(0, 5);
          if (v !== e.target.value) immutableSetFormData({ beneficiaryEvaluationPin: v });
        },
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
        id: "beneficiaryEvaluationPin",
        type: "text",
        required: true,
        message: "Beneficiary evaluation PIN (required). Exactly 5 digits. All beneficiaries use this PIN to submit feedback for this event.",
        placeholder: "5 digits",
        inputProps: { maxLength: 5, inputMode: "numeric" as const },
        onUse: (e: { target: { value: string } }) => {
          const v = (e.target.value || "").replace(/\D/g, "").slice(0, 5);
          if (v !== e.target.value) immutableSetFormData({ beneficiaryEvaluationPin: v });
        },
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
    { type: "section", message: "Monitoring and Evaluation Mechanics / Plan" },
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
                key="external-form"
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

