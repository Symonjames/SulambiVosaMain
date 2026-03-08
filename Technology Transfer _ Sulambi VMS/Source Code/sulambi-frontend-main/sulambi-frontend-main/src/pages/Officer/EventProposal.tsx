import { useContext, useEffect, useState } from "react";
import CustomButton from "../../components/Buttons/CustomButton";
import EventProposalForm from "../../components/Forms/EventProposalForm";
import TextHeader from "../../components/Headers/TextHeader";
import TextSubHeader from "../../components/Headers/TextSubHeader";
import CustomDropdown from "../../components/Inputs/CustomDropdown";
import DataTable from "../../components/Tables/DataTable";
import PageLayout from "../PageLayout";
import AddIcon from "@mui/icons-material/Add";
import RemoveRedEyeIcon from "@mui/icons-material/RemoveRedEye";
import PublicIcon from "@mui/icons-material/Public";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";

import {
  deleteMyEvents,
  getAllEvents,
  publicizeExternalEvent,
  publicizeInternalEvent,
  submitExternalEvent,
  submitInternalEvent,
  updateExternalEvent,
  updateInternalEvent,
} from "../../api/events";
import {
  ExternalEventProposalType,
  InternalEventProposalType,
} from "../../interface/types";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { SnackbarContext } from "../../contexts/SnackbarProvider";
import MenuButtonTemplate from "../../components/Menu/MenuButtonTemplate";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import BarChartIcon from "@mui/icons-material/BarChart";
import BorderColorIcon from "@mui/icons-material/BorderColor";
import EditIcon from "@mui/icons-material/Edit";
import FeedbackIcon from "@mui/icons-material/Feedback";
import Chip from "../../components/Chips/Chip";
import FormDataLoaderModal from "../../components/Modal/FormDataLoaderModal";
import PrimaryButton from "../../components/Buttons/PrimaryButton";
import FindInPageIcon from "@mui/icons-material/FindInPage";
import EvaluationList from "../../components/Popups/EvaluationList";
import LatentAnalysisList from "../../components/Popups/LatentAnalysisList";
import { useSearchParams } from "react-router-dom";
import FeedbackForm from "../../components/Forms/FeedbackForm";
import ReportForm from "../../components/Forms/ReportForm";
import SignatoriesForm from "../../components/Forms/SignatoriesForm";
import HistoryEduIcon from "@mui/icons-material/HistoryEdu";
import LoadingSpinner from "../../components/Loading/LoadingSpinner";
import { toJsonString } from "../../utils/looseJson";
import { getFromSessionObfuscated } from "../../utils/storage";

const EventProposal = () => {
  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const [searchParams] = useSearchParams();

  const [showFormPreview, setShowFormPreview] = useState(false);
  const [searchVal, setSearchVal] = useState("");
  const [debouncedSearchVal, setDebouncedSearchVal] = useState("");
  const [openUpdateSignatories, setOpenUpdateSignatories] = useState(false);
  const [signatoryId, setSignatoryId] = useState<number | null>(null);

  const [allEventsData, setAllEventsData] = useState<any[]>([]);
  const [tableData, setTableData] = useState<any>([]);
  const [refreshTable, setRefreshTable] = useState(0);
  const [loading, setLoading] = useState(true);

  const [openProposalForm, setOpenProposalForm] = useState(false);
  const [editProposal, setEditProposal] = useState(false);

  const [eventType, setEventType] = useState<[number, string] | undefined>(
    undefined
  );
  const [selectedFormData, setSelectedFormData] = useState<any>({});
  const [selectedFormType, setSelectedFormType] = useState<
    "external" | "internal" | ""
  >("");

  const [searchStatus, setSearchStatus] = useState(
    searchParams.get("status") ?? ""
  );
  const [searchFilter, setSearchFilter] = useState({
    type: "",
    searchText: "",
  });
  const [searchYear, setSearchYear] = useState<string>("");

  const [showEvaluationList, setShowEvaluationList] = useState(false);
  const [showEventAnalysis, setShowEventAnalysis] = useState(false);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [showReportForm, setShowReportForm] = useState(false);
  const [reportTarget, setReportTarget] = useState<{ id: number; type: "external" | "internal" } | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchVal(searchVal), 250);
    return () => clearTimeout(timer);
  }, [searchVal]);

  const normalizeText = (value: unknown) =>
    String(value ?? "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();

  const chipMap = {
    editing: <Chip bgcolor="blue" label="editing" color="white" />,
    submitted: (
      <Chip bgcolor="#a3a300" label="submitted proposal" color="white" />
    ),
    accepted: <Chip bgcolor="#2f7a00" label="approved event" color="white" />,
    rejected: (
      <Chip bgcolor="#c10303" label="rejected proposal" color="white" />
    ),
  };

  const publicChipMap = {
    0: <Chip bgcolor="blue" label="not public" color="white" />,
    1: <Chip bgcolor="#2f7a00" label="public" color="white" />,
  };

  const submitExternalOnClick = async (eventId: any) => {
    try {
      await submitExternalEvent(eventId);
      showSnackbarMessage("Successfully submitted proposal!", "success");
      setRefreshTable(refreshTable + 1);
    } catch {
      showSnackbarMessage("An Error Occured while submitting proposal");
      setRefreshTable(refreshTable + 1);
    }
  };

  const submitInternalOnClick = async (eventId: any) => {
    try {
      await submitInternalEvent(eventId);
      showSnackbarMessage("Successfully submitted proposal!", "success");
      setRefreshTable(refreshTable + 1);
    } catch {
      showSnackbarMessage("An Error Occured while submitting proposal");
      setRefreshTable(refreshTable + 1);
    }
  };

  const makePublicOnClick = async () => {
    try {
      if (selectedFormType === "external") {
        await publicizeExternalEvent(selectedFormData.id);
      } else {
        await publicizeInternalEvent(selectedFormData.id);
      }
      showSnackbarMessage("Event is now public (shown on homepage)", "success");
    } catch {
      showSnackbarMessage(
        "An error occurred while making the event public"
      );
    } finally {
      setRefreshTable(refreshTable + 1);
      setShowFormPreview(false);
    }
  };

  const deleteMyEventsOnClick = async () => {
    const confirmed = window.confirm(
      "This will permanently delete ALL events you created, including related reports, requirements, and evaluations. This cannot be undone. Continue?"
    );
    if (!confirmed) return;

    try {
      const response = await deleteMyEvents();
      const deleted = response?.data?.deleted ?? {};
      const total =
        response?.data?.totalEventsDeleted ??
        (Number(deleted.externalEvents || 0) + Number(deleted.internalEvents || 0));

      showSnackbarMessage(
        `Deleted ${total} event(s) you created permanently.`,
        "success"
      );
    } catch (err: any) {
      const apiMessage = err?.response?.data?.message;
      showSnackbarMessage(
        apiMessage || "An error occurred while deleting your events.",
        "error"
      );
    } finally {
      setRefreshTable((prev) => prev + 1);
    }
  };

  useEffect(() => {
    (async function () {
      try {
        setLoading(true);
        const events = await getAllEvents();
        const sortedEventData: (
          | ExternalEventProposalType
          | InternalEventProposalType
        )[] = events.data.events;
        setAllEventsData(sortedEventData);
        setLoading(false);
      } catch (err: any) {
        console.log(err);
        setAllEventsData([]);
        setLoading(false);
      }
    })();
  }, [refreshTable]);

  useEffect(() => {
    const terms = normalizeText(debouncedSearchVal).split(" ").filter(Boolean);
    setTableData(
      allEventsData
        .filter((event: any) => {
          if (!terms.length) return true;
          const haystack = normalizeText(
            [
              event.title,
              event.status,
              event.eventTypeIndicator,
              event.createdBy?.username,
            ].join(" ")
          );
          return terms.every((term) => haystack.includes(term));
        })
        .filter((event: any) => {
          if (searchStatus === "") return true;
          return event.status === searchStatus;
        })
        .filter((event: any) => {
          if (searchFilter.type === "") return true;
          return event.eventTypeIndicator === searchFilter.type;
        })
        .map((eventdata: any) => [
              eventdata.title,
              eventdata.eventTypeIndicator,
              chipMap[
                eventdata.status as
                  | "editing"
                  | "submitted"
                  | "accepted"
                  | "rejected"
              ],
              eventdata.toPublic ? publicChipMap[1] : publicChipMap[0],
              eventdata.status === "editing" ? (
                <MenuButtonTemplate
                  items={[
                    {
                      label: "View",
                      icon: <RemoveRedEyeIcon />,
                      onClick: () => {
                        setSelectedFormType(eventdata.eventTypeIndicator);
                        setSelectedFormData(eventdata);
                        setShowFormPreview(true);
                      },
                    },
                    {
                      label: "Edit",
                      icon: <EditIcon />,
                      onClick: () => {
                        setOpenProposalForm(true);
                        setEventType([
                          eventdata.id,
                          eventdata.eventTypeIndicator,
                        ]);
                        setFormData(eventdata);
                        setEditProposal(true);
                      },
                    },
                    {
                      label: "Submit",
                      icon: <ArrowUpwardIcon />,
                      onClick: () =>
                        eventdata.eventTypeIndicator === "internal"
                          ? submitInternalOnClick(eventdata.id)
                          : submitExternalOnClick(eventdata.id),
                    },
                  ]}
                />
              ) : (
                <MenuButtonTemplate
                  items={[
                    {
                      label: "View",
                      icon: <RemoveRedEyeIcon />,
                      onClick: () => {
                        setSelectedFormType(eventdata.eventTypeIndicator);
                        setSelectedFormData(eventdata);
                        setShowFormPreview(true);
                      },
                    },
                    ...(eventdata.status === "accepted" && !eventdata.toPublic
                      ? [
                          {
                            label: "Make Public",
                            icon: <PublicIcon />,
                            onClick: async () => {
                              try {
                                if (eventdata.eventTypeIndicator === "internal") {
                                  await publicizeInternalEvent(eventdata.id);
                                } else {
                                  await publicizeExternalEvent(eventdata.id);
                                }
                                showSnackbarMessage("Event is now public (shown on homepage)", "success");
                                setRefreshTable((r) => r + 1);
                              } catch {
                                showSnackbarMessage("An error occurred while making the event public", "error");
                                setRefreshTable((r) => r + 1);
                              }
                            },
                          },
                        ]
                      : []),
                    {
                      label: "View Evaluations",
                      icon: <FindInPageIcon />,
                      onClick: () => {
                        setSelectedFormType("external");
                        setSelectedFormData(eventdata);
                        setShowEvaluationList(true);
                      },
                    },
                    {
                      label: "View Analysis",
                      icon: <BarChartIcon />,
                      onClick: () => {
                        setSelectedFormType("external");
                        setSelectedFormData(eventdata);
                        setShowEventAnalysis(true);
                      },
                    },
                    ...(eventdata.status === "accepted" && !eventdata.hasReport
                      ? [
                          {
                            label: "Submit a Report",
                            icon: <BarChartIcon />,
                            onClick: () => {
                              setReportTarget({
                                id: eventdata.id,
                                type: eventdata.eventTypeIndicator === "internal" ? "internal" : "external",
                              });
                              setShowReportForm(true);
                            },
                          },
                        ]
                      : []),
                  ]}
                />
              ),
            ])
    );
  }, [allEventsData, debouncedSearchVal, searchFilter.type, searchStatus]);

  const ModRightComponents = [
    <CustomDropdown
      label="Filter Status"
      width="200px"
      initialValue={searchStatus ?? ""}
      menu={[
        { key: "All", value: "" },
        { key: "Editing", value: "editing" },
        { key: "Submitted", value: "submitted" },
        { key: "Approved", value: "accepted" },
        { key: "Rejected", value: "rejected" },
      ]}
      onChange={(event) => {
        setSearchStatus(event.target.value);
      }}
    />,
    <CustomDropdown
      label="Filter Type"
      width="200px"
      menu={[
        { key: "All", value: "" },
        { key: "Internal", value: "internal" },
        { key: "External", value: "external" },
      ]}
      onChange={(event) => {
        setSearchFilter({
          ...searchFilter,
          type: event.target.value,
        });
      }}
    />,
  ];

  const ModLeftComponents = [
    <CustomButton
      label="New Event Proposal"
      startIcon={<AddIcon />}
      hoverSx={{
        backgroundColor: "white",
        color: "black",
      }}
      sx={{
        bgcolor: "var(--text-landing)",
        border: "1px solid green",
        borderRadius: "10px",
        color: "white",
        padding: "0px 20px",
      }}
      onClick={() => {
        setOpenProposalForm(true);
        setFormData({});
      }}
    />,
    <CustomButton
      label="Delete All My Events"
      startIcon={<DeleteForeverIcon />}
      hoverSx={{
        backgroundColor: "#7f1d1d",
        color: "white",
      }}
      sx={{
        bgcolor: "#991b1b",
        border: "1px solid #7f1d1d",
        borderRadius: "10px",
        color: "white",
        padding: "0px 20px",
      }}
      onClick={deleteMyEventsOnClick}
    />,
  ];

  return (
    <>
      <EventProposalForm
        eventType={eventType}
        open={openProposalForm}
        hideSubmit={editProposal}
        setOpen={setOpenProposalForm}
        onSubmit={() => setRefreshTable(refreshTable + 1)}
        onClose={() => {
          setEventType(undefined);
          setEditProposal(false);
          setFormData({});
        }}
        zval={5}
        componentsBeforeSubmit={
          editProposal ? (
            <PrimaryButton
              label="Update"
              startIcon={<EditIcon />}
              onClick={async () => {
                if (eventType) {
                  if (eventType[1] == "external") {
                    // Process formData the same way as submitCallback - stringify objects
                    const processedFormData = { ...formData };
                    // Persist checkbox/selection fields as JSON strings for backend storage
                    if (processedFormData.sdg && typeof processedFormData.sdg === "object") {
                      processedFormData.sdg = toJsonString(processedFormData.sdg, "[]");
                    }
                    if (processedFormData.extensionServiceType && typeof processedFormData.extensionServiceType === "object") {
                      processedFormData.extensionServiceType = toJsonString(processedFormData.extensionServiceType, "[]");
                    }
                    if (processedFormData.externalServiceType && typeof processedFormData.externalServiceType === "object") {
                      processedFormData.externalServiceType = toJsonString(processedFormData.externalServiceType, "[]");
                    }
                    if (processedFormData.eventProposalType && typeof processedFormData.eventProposalType === "object") {
                      processedFormData.eventProposalType = toJsonString(processedFormData.eventProposalType, "[]");
                    }
                    if (processedFormData.financialPlan && typeof processedFormData.financialPlan === 'object') {
                      processedFormData.financialPlan = JSON.stringify(processedFormData.financialPlan);
                    }
                    // Stringify evaluationMechanicsPlan for external events (includes objective labels)
                    if (processedFormData.evaluationMechanicsPlan && typeof processedFormData.evaluationMechanicsPlan === 'object') {
                      processedFormData.evaluationMechanicsPlan = JSON.stringify(processedFormData.evaluationMechanicsPlan);
                    }
                    updateExternalEvent(eventType[0], processedFormData)
                      .then(() => {
                        showSnackbarMessage(
                          "Successfully updated external event data",
                          "info"
                        );
                      })
                      .catch(() => {
                        showSnackbarMessage(
                          "An error occured in updating external event data",
                          "error"
                        );
                      })
                      .finally(() => {
                        setRefreshTable(refreshTable + 1);
                        setOpenProposalForm(false);
                      });
                  }

                  if (eventType[1] == "internal") {
                    // Flush any pending Gantt table updates synchronously before processing
                    // This ensures workPlan is saved immediately, not waiting for debounce
                    if (typeof window !== 'undefined') {
                      const flushFn = (window as any)[`__flushGantt_workPlan`];
                      if (flushFn && typeof flushFn === 'function') {
                        console.log("[UPDATE_EVENT] Flushing workPlan updates synchronously");
                        flushFn();
                        // Small delay to let the flush complete
                        await new Promise(resolve => setTimeout(resolve, 50));
                      }
                    }
                    
                    // Get the latest formData - try reading from sessionStorage first since FormDataProvider saves there
                    // This ensures we get the most up-to-date workPlan even if React state is stale
                    let latestFormData = formData;
                    try {
                      const storedFormData = getFromSessionObfuscated<Record<string, any>>('formData', null);
                      if (storedFormData && storedFormData.workPlan) {
                        // If sessionStorage has workPlan data, check if it's more up-to-date
                        const storedWorkPlan = storedFormData.workPlan;
                        const currentWorkPlan = latestFormData.workPlan;
                        
                        // If stored workPlan is an object with data, or if current is empty/undefined, use stored
                        if ((typeof storedWorkPlan === 'object' && Object.keys(storedWorkPlan).length > 0) ||
                            (!currentWorkPlan || currentWorkPlan === "{}" || (typeof currentWorkPlan === 'object' && Object.keys(currentWorkPlan).length === 0))) {
                          latestFormData = { ...latestFormData, workPlan: storedWorkPlan };
                          console.log("[UPDATE_EVENT] Using workPlan from sessionStorage (more up-to-date)", Object.keys(storedWorkPlan).length, "rows");
                        }
                      }
                    } catch (e) {
                      console.warn("[UPDATE_EVENT] Could not read from sessionStorage:", e);
                    }
                    
                    // Debug logging
                    console.log("[UPDATE_EVENT] formData.workPlan before processing:", typeof latestFormData.workPlan, latestFormData.workPlan ? (typeof latestFormData.workPlan === 'object' ? Object.keys(latestFormData.workPlan).length + ' keys' : latestFormData.workPlan.substring(0, 100)) : 'undefined');
                    
                    // Process formData the same way as submitCallback - stringify objects
                    const processedFormData = { ...latestFormData };
                    if (processedFormData.eventProposalType && typeof processedFormData.eventProposalType === "object") {
                      processedFormData.eventProposalType = toJsonString(processedFormData.eventProposalType, "[]");
                    }
                    // Always ensure workPlan is included and properly stringified
                    // Handle both object and string cases, and ensure it's never undefined
                    if (processedFormData.workPlan) {
                      if (typeof processedFormData.workPlan === 'object') {
                        processedFormData.workPlan = JSON.stringify(processedFormData.workPlan);
                        console.log("[UPDATE_EVENT] workPlan was object, stringified. Length:", processedFormData.workPlan.length);
                      } else if (typeof processedFormData.workPlan === 'string') {
                        // Already a string, use as-is
                        console.log("[UPDATE_EVENT] workPlan was already string. Length:", processedFormData.workPlan.length);
                      } else {
                        // Fallback to empty object if invalid type
                        processedFormData.workPlan = "{}";
                        console.log("[UPDATE_EVENT] workPlan had invalid type, set to {}");
                      }
                    } else {
                      // If workPlan is missing, set to empty object string
                      processedFormData.workPlan = "{}";
                      console.log("[UPDATE_EVENT] workPlan was missing/undefined, set to {}");
                    }
                    console.log("[UPDATE_EVENT] Final workPlan being sent:", processedFormData.workPlan.substring(0, 100));
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
                    
                    updateInternalEvent(eventType[0], processedFormData)
                      .then(() => {
                        showSnackbarMessage(
                          "Successfully updated internal event data",
                          "info"
                        );
                      })
                      .catch((err) => {
                        console.error("Error updating internal event:", err);
                        showSnackbarMessage(
                          "An error occured in updating internal event data",
                          "error"
                        );
                      })
                      .finally(() => {
                        setRefreshTable(refreshTable + 1);
                        setOpenProposalForm(false);
                      });
                  }
                }
              }}
            />
          ) : (
            <></>
          )
        }
      />
      {showFeedbackForm && selectedFormType && selectedFormData && (
        <FeedbackForm
          open={showFeedbackForm}
          setOpen={setShowFeedbackForm}
          feedbackId={selectedFormData.feedback_id}
          eventId={selectedFormData.id}
          eventType={selectedFormType as "external" | "internal"}
          viewOnly
        />
      )}
      <EvaluationList
        open={showEvaluationList}
        selectedFormData={selectedFormData}
        selectedFormType={selectedFormType as "external" | "internal"}
        setOpen={setShowEvaluationList}
      />
      <LatentAnalysisList
        eventId={selectedFormData.id}
        eventType={selectedFormType as "external" | "internal"}
        open={showEventAnalysis}
        setOpen={setShowEventAnalysis}
      />
      {reportTarget && (
        <ReportForm
          open={showReportForm}
          setOpen={setShowReportForm}
          eventId={reportTarget.id}
          type={reportTarget.type}
          onSubmit={() => {
            setReportTarget(null);
            setShowReportForm(false);
            setRefreshTable(refreshTable + 1);
          }}
        />
      )}
      {signatoryId && (
        <SignatoriesForm
          signatoryId={signatoryId}
          open={openUpdateSignatories}
          setOpen={setOpenUpdateSignatories}
          onSave={() => {
            setOpenUpdateSignatories(false);
            setRefreshTable(refreshTable + 1);
          }}
        />
      )}
      <FormDataLoaderModal
        data={selectedFormData}
        open={showFormPreview}
        setOpen={setShowFormPreview}
        // hidePrintButton={
        //   // !(selectedFormData && selectedFormData.status === "accepted")
        // }
        formType={
          selectedFormType === "external" ? "externalEvent" : "internalEvent"
        }
        beforePrintComponent={
          <>
            {selectedFormData &&
            selectedFormData.status === "accepted" &&
            !selectedFormData.toPublic ? (
              <PrimaryButton
                label="Make Public"
                startIcon={<PublicIcon />}
                onClick={makePublicOnClick}
              />
            ) : selectedFormData && !!selectedFormData.feedback_id ? (
              <>
                <PrimaryButton
                  label="Edit Form"
                  startIcon={<BorderColorIcon />}
                  onClick={() => {
                    setFormData(selectedFormData);
                    setEventType([
                      selectedFormData.id,
                      selectedFormData.eventTypeIndicator,
                    ]);
                    setOpenProposalForm(true);
                    setEditProposal(true);
                  }}
                />
                <PrimaryButton
                  label="Show Feedback"
                  startIcon={<FeedbackIcon />}
                  onClick={() => {
                    setShowFeedbackForm(true);
                  }}
                />
              </>
            ) : (
              <></>
            )}
            {selectedFormData && selectedFormData === "accepted" && (
              <>
                <PrimaryButton
                  label="View Evaluations"
                  icon={<FindInPageIcon />}
                  onClick={() => {
                    setShowEvaluationList(true);
                  }}
                />
                <PrimaryButton
                  label="View Analysis"
                  icon={<BarChartIcon />}
                  onClick={() => {
                    setShowEventAnalysis(true);
                  }}
                />
              </>
            )}
            {selectedFormData && selectedFormData.signatoriesId && (
              <PrimaryButton
                label="Update Signatories"
                startIcon={<HistoryEduIcon />}
                onClick={() => {
                  setSignatoryId(selectedFormData.signatoriesId?.id ?? null);
                  setOpenUpdateSignatories(true);
                }}
              />
            )}
          </>
        }
      />
      <PageLayout page="event-proposal">
        <TextHeader>EVENT PROPOSAL</TextHeader>
        <TextSubHeader>Track and Create your proposal here</TextSubHeader>
        {loading ? (
          <LoadingSpinner message="Loading event proposals..." />
        ) : (
          <DataTable
            title="Event Proposals"
            fields={["Event title", "Type", "Status", "Public Status", "Actions"]}
            data={tableData}
            componentBeforeSearch={ModRightComponents}
            componentOnLeft={ModLeftComponents}
            searchPlaceholder="Search name of event"
            searchOnSubmitOnly
            onSearch={(key) => {
              setSearchVal(key);
            }}
          />
        )}
      </PageLayout>
    </>
  );
};

export default EventProposal;
