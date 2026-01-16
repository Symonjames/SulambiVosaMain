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

import {
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

const EventProposal = () => {
  const { formData, setFormData } = useContext(FormDataContext);
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const [searchParams] = useSearchParams();

  const [showFormPreview, setShowFormPreview] = useState(false);
  const [searchVal, setSearchVal] = useState("");
  const [openUpdateSignatories, setOpenUpdateSignatories] = useState(false);
  const [signatoryId, setSignatoryId] = useState<number | null>(null);

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

  const [showEvaluationList, setShowEvaluationList] = useState(false);
  const [showEventAnalysis, setShowEventAnalysis] = useState(false);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [showReportForm, setShowReportForm] = useState(false);
  const [reportTarget, setReportTarget] = useState<{ id: number; type: "external" | "internal" } | null>(null);

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
    0: <Chip bgcolor="blue" label="not for public" color="white" />,
    1: <Chip bgcolor="#2f7a00" label="for public" color="white" />,
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
      showSnackbarMessage("Successfully made the event to public", "success");
    } catch {
      showSnackbarMessage(
        "An Error Occured while making this event available to public"
      );
    } finally {
      setRefreshTable(refreshTable + 1);
      setShowFormPreview(false);
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

        // const externalEventData: ExternalEventProposalType[] =
        //   events.data.external;
        // const internalEventData: InternalEventProposalType[] =
        //   events.data.internal;

        setTableData(
          sortedEventData
            .filter((event) => {
              if (searchVal === "") return true;
              return (
                event.title.toLowerCase().includes(searchVal) ||
                event.status.toLowerCase().includes(searchVal)
              );
            })
            .filter((event) => {
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
        setLoading(false);
      } catch (err: any) {
        console.log(err);
        setLoading(false);
      }
    })();
  }, [refreshTable, searchFilter, searchVal, searchStatus]);

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
              onClick={() => {
                if (eventType) {
                  if (eventType[1] == "external") {
                    // Process formData the same way as submitCallback - stringify objects
                    const processedFormData = { ...formData };
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
                    // Process formData the same way as submitCallback - stringify objects
                    const processedFormData = { ...formData };
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
            selectedFormData.toPublic === 0 ? (
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
            onSearch={(key) => {
              setSearchVal(key.toLowerCase());
            }}
          />
        )}
      </PageLayout>
    </>
  );
};

export default EventProposal;
