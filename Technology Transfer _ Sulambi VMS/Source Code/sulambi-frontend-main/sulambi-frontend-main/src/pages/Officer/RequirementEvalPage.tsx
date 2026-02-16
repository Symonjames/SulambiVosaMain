import { useContext, useEffect, useMemo, useState } from "react";
import TextHeader from "../../components/Headers/TextHeader";
import TextSubHeader from "../../components/Headers/TextSubHeader";
import DataTable from "../../components/Tables/DataTable";
import PageLayout from "../PageLayout";
import {
  acceptRequirement,
  getAllRequirements,
  rejectRequirement,
} from "../../api/requirements";
import { getAllEvents } from "../../api/events";
import { RequirementsDataType } from "../../interface/types";
import Chip from "../../components/Chips/Chip";
import MenuButtonTemplate from "../../components/Menu/MenuButtonTemplate";
import { SnackbarContext } from "../../contexts/SnackbarProvider";
import { AccountDetailsContext } from "../../contexts/AccountDetailsProvider";
import RequirementForm from "../../components/Forms/RequirementForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import CustomDropdown from "../../components/Inputs/CustomDropdown";
import { useNavigate } from "react-router-dom";
import LoadingSpinner from "../../components/Loading/LoadingSpinner";
import { Typography, Box } from "@mui/material";

// Track IDs we just accepted/rejected so the list shows correct status even if refetch returns stale data
const recentlyAcceptedIds = { current: new Set<string>() };
const recentlyRejectedIds = { current: new Set<string>() };

const RequirementEvalPage = () => {
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const { accountDetails, sessionChecked } = useContext(AccountDetailsContext);
  const { setFormData } = useContext(FormDataContext);
  const navigate = useNavigate();

  const [searchStatus, setSearchStatus] = useState(3);
  const [searchVal, setSearchVal] = useState("");
  const [debouncedSearchVal, setDebouncedSearchVal] = useState("");
  const [allRequirementsData, setAllRequirementsData] = useState<RequirementsDataType[]>([]);
  const [forceRefresh, setForceRefresh] = useState(0);
  const [loading, setLoading] = useState(true);
  /** Filter by event: null = all events; otherwise { id, type, title } */
  const [eventFilter, setEventFilter] = useState<{ id: number; type: string; title: string } | null>(null);
  const [eventsList, setEventsList] = useState<{ id: number; type: string; title: string }[]>([]);

  const [selectedFormData, setSelectedFormData] = useState<any>({});
  const [viewFormData, setViewFormData] = useState(false);

  // Auth: session in httpOnly cookie; accountDetails from context (sessionStorage obfuscated or /auth/me)
  useEffect(() => {
    if (!sessionChecked) return;
    const { username, accountType } = accountDetails;
    if (!username || !accountType) {
      showSnackbarMessage("Please log in to access this page", "warning");
      navigate("/login");
      return;
    }
    if (accountType !== "officer" && accountType !== "admin") {
      showSnackbarMessage("You don't have permission to access this page", "error");
      navigate("/login");
      return;
    }
  }, [sessionChecked, accountDetails, navigate, showSnackbarMessage]);

  // Debounce search input to improve performance
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchVal(searchVal);
    }, 300); // 300ms delay

    return () => clearTimeout(timer);
  }, [searchVal]);

  // Load events for "Filter by event" dropdown (accepted so they can have members)
  useEffect(() => {
    getAllEvents()
      .then((res) => {
        const events: typeof eventsList = [];
        const list = res?.data?.events ?? [];
        for (const e of list) {
          const status = (e?.status ?? "").toString().toLowerCase();
          if (status === "accepted" && e?.id != null && e?.title != null) {
            events.push({
              id: Number(e.id),
              type: (e?.eventTypeIndicator ?? e?.type ?? "external").toString(),
              title: String(e.title),
            });
          }
        }
        setEventsList(events);
      })
      .catch(() => setEventsList([]));
  }, []);

  // Fetch requirements only when forceRefresh changes (initial load or after accept/reject). Filtering is client-side.
  useEffect(() => {
    setLoading(true);
    getAllRequirements()
      .then((response) => {
        if (!response?.data?.data) {
          showSnackbarMessage("Invalid response format from server", "error");
          setAllRequirementsData([]);
          setLoading(false);
          return;
        }
        const data = response.data.data;
        if (!Array.isArray(data)) {
          showSnackbarMessage("Requirements data format error", "error");
          setAllRequirementsData([]);
          setLoading(false);
          return;
        }
        setAllRequirementsData(data);
        setLoading(false);
        recentlyAcceptedIds.current.clear();
        recentlyRejectedIds.current.clear();
      })
      .catch((err) => {
        if (err.response?.status === 403) {
          const msg = err.response?.data?.message || "";
          if (msg.includes("Unauthorized") || msg.includes("Token")) {
            showSnackbarMessage("Please log in to view requirements. Your session may have expired.", "error");
            setTimeout(() => navigate("/login"), 2000);
          } else {
            showSnackbarMessage(`Access denied: ${msg}`, "error");
          }
        } else {
          showSnackbarMessage(`An error occurred while fetching requirements: ${err.message || "Unknown error"}`, "error");
        }
        setAllRequirementsData([]);
        setLoading(false);
      });
  }, [forceRefresh, showSnackbarMessage, navigate]);

  const chipMap = useMemo(() => ({
    notEvaluated: <Chip bgcolor="blue" label="not-evaluated" color="white" />,
    approved: <Chip bgcolor="#2f7a00" label="approved" color="white" />,
    rejected: <Chip bgcolor="#c10303" label="rejected" color="white" />,
  }), []);

  const tableData = useMemo(() => {
    if (!allRequirementsData.length) return [];

    const normalizedData = allRequirementsData.map((req: any) => {
      let eventId = req.eventId || req.eventid;
      if (typeof eventId === "number" || typeof eventId === "string") {
        eventId = { id: eventId, title: `Event ID ${eventId}`, status: "unknown" };
      }
      const idStr = String(req.id ?? "");
      let accepted: number | null;
      if (recentlyAcceptedIds.current.has(idStr)) accepted = 1;
      else if (recentlyRejectedIds.current.has(idStr)) accepted = 0;
      else {
        const raw = req.accepted;
        accepted = raw === true || raw === 1 || raw === "1" || String(raw).trim() === "1" ? 1
          : raw === false || raw === 0 || raw === "0" || String(raw).trim() === "0" ? 0
          : null;
      }
      return { ...req, eventId, accepted };
    });

    const afterSearch = normalizedData.filter((req) => {
      if (!debouncedSearchVal || !debouncedSearchVal.trim()) return true;
      const terms = debouncedSearchVal.toLowerCase().trim().split(/\s+/).filter(Boolean);
      if (!terms.length) return true;
      const text = [
        req.eventId?.title ?? "Unknown Event",
        req.fullname ?? "",
        req.srcode ?? "",
        req.collegeDept ?? "",
        req.email ?? "",
        req.campus ?? "",
        req.yrlevelprogram ?? "",
        req.address ?? "",
        req.contactNum ?? "",
        req.type ?? "",
      ].join(" ").toLowerCase();
      return terms.every((t) => text.includes(t));
    });

    const afterStatus = afterSearch.filter((req) => {
      if (searchStatus === 3) return true;
      if (searchStatus === 2) return req.accepted === null;
      return req.accepted === searchStatus;
    });

    const afterEvent = eventFilter
      ? afterStatus.filter((req) => {
          const reqId = req.eventId != null && typeof req.eventId === "object" ? req.eventId.id : req.eventId;
          return Number(reqId) === eventFilter.id && (req.type ?? "external") === eventFilter.type;
        })
      : afterStatus;

    return afterEvent.map((req) => [
      req.eventId?.title || "Unknown Event",
      req.fullname || "N/A",
      req.accepted === 0 ? chipMap.rejected : req.accepted === 1 ? chipMap.approved : chipMap.notEvaluated,
      req.accepted === null ? (
        <MenuButtonTemplate
          items={[
            {
              label: "View Requirement",
              onClick: () => {
                setSelectedFormData(req);
                setFormData(req);
                setViewFormData(true);
              },
            },
            {
              label: "Accept",
              onClick: () => {
                const idStr = String(req.id ?? "");
                acceptRequirement(req.id)
                  .then(() => {
                    recentlyAcceptedIds.current.add(idStr);
                    recentlyRejectedIds.current.delete(idStr);
                    setAllRequirementsData((prev) => prev.map((r) => (String(r.id) === idStr ? { ...r, accepted: 1 } : r)));
                    showSnackbarMessage("Successfully accepted requirement", "success");
                    setForceRefresh((n) => n + 1);
                  })
                  .catch((err) => {
                    if (err.response?.status === 401 || err.response?.status === 403) {
                      showSnackbarMessage("Please log in as officer or admin to approve requirements.", "error");
                    } else {
                      showSnackbarMessage(`Accept failed: ${err.response?.data?.message || "Unknown"}`, "error");
                    }
                  });
              },
            },
            {
              label: "Reject",
              onClick: () => {
                const idStr = String(req.id ?? "");
                rejectRequirement(req.id)
                  .then(() => {
                    recentlyRejectedIds.current.add(idStr);
                    recentlyAcceptedIds.current.delete(idStr);
                    setAllRequirementsData((prev) => prev.map((r) => (String(r.id) === idStr ? { ...r, accepted: 0 } : r)));
                    showSnackbarMessage("Successfully rejected requirement", "success");
                    setForceRefresh((n) => n + 1);
                  })
                  .catch((err) => {
                    if (err.response?.status === 401 || err.response?.status === 403) {
                      showSnackbarMessage("Please log in as officer or admin to reject requirements.", "error");
                    } else {
                      showSnackbarMessage(`Reject failed: ${err.response?.data?.message || "Unknown"}`, "error");
                    }
                  });
              },
            },
          ]}
        />
      ) : (
        <MenuButtonTemplate
          items={[
            { label: "View Requirement", onClick: () => { setSelectedFormData(req); setFormData(req); setViewFormData(true); } },
            { label: "Show Evaluation Form", onClick: () => navigate(`/evaluation/${req.id}`) },
          ]}
        />
      ),
    ]);
  }, [allRequirementsData, debouncedSearchVal, searchStatus, eventFilter, chipMap, setFormData, showSnackbarMessage, navigate]);

  const ModRightComponents = [
    <CustomDropdown
      key={`filter-event-${eventFilter ? `${eventFilter.id}-${eventFilter.type}` : "all"}`}
      label="Filter by event"
      width="220px"
      initialValue={eventFilter ? `${eventFilter.id}-${eventFilter.type}` : ""}
      menu={[
        { key: "All events", value: "" },
        ...eventsList.map((e) => ({
          key: e.title,
          value: `${e.id}-${e.type}`,
        })),
      ]}
      onChange={(e) => {
        const val = e.target.value;
        if (!val) {
          setEventFilter(null);
          return;
        }
        const [idStr, type] = val.split("-");
        const id = parseInt(idStr, 10);
        const ev = eventsList.find((x) => x.id === id && x.type === type);
        setEventFilter(ev ?? null);
      }}
    />,
    <CustomDropdown
      key="filter-status-dropdown"
      label="Filter Status"
      width="200px"
      menu={[
        { key: "All", value: 3 },
        { key: "Not Evaluated", value: 2 },
        { key: "Approved", value: 1 },
        { key: "Rejected", value: 0 },
      ]}
      onChange={(event) => {
        setSearchStatus(parseInt(event.target.value));
      }}
    />,
  ];

  if (loading) {
    return (
      <PageLayout page="requirement-evaluation">
        <TextHeader>REQUIREMENT EVALUATION</TextHeader>
        <TextSubHeader>Evaluate participant requirements here</TextSubHeader>
        <LoadingSpinner message="Loading requirements..." />
      </PageLayout>
    );
  }

  return (
    <>
      <RequirementForm
        preventLoadingCache
        viewOnly
        eventId={selectedFormData.eventId?.id || selectedFormData.eventId || 0}
        eventType={selectedFormData.type || "external"}
        open={viewFormData}
        setOpen={setViewFormData}
      />
      <PageLayout page="requirement-evaluation">
        <TextHeader>REQUIREMENT EVALUATION</TextHeader>
        <TextSubHeader>Evaluate participant requirements here</TextSubHeader>
        {tableData.length === 0 ? (
          <div style={{ 
            padding: "40px", 
            textAlign: "center",
            color: "var(--text-landing, #666)"
          }}>
            <Typography variant="h6" style={{ marginBottom: "10px" }}>
              {eventFilter ? `No members for "${eventFilter.title}"` : "No requirements found"}
            </Typography>
            <Typography variant="body2" style={{ marginBottom: "20px" }}>
              {eventFilter
                ? "No members have joined this event yet. Members with accounts can see and join all approved events from their Events page (even if not on homepage). Use \"Make Public\" to also list the event on the public homepage."
                : debouncedSearchVal || searchStatus !== 3
                  ? "Try adjusting your search or filter criteria"
                  : "Members appear here after they join events. Members with accounts see all approved events on their Events page. \"Make Public\" only controls whether the event appears on the public homepage for visitors."}
            </Typography>
            {debouncedSearchVal && (
              <Typography variant="caption" style={{ 
                display: "block",
                marginTop: "10px",
                color: "#999",
                fontSize: "0.85rem"
              }}>
                Search: "{debouncedSearchVal}"
              </Typography>
            )}
          </div>
        ) : (
          <>
            {(debouncedSearchVal || searchStatus !== 3) && (
              <Box sx={{ 
                padding: "10px 20px", 
                backgroundColor: "#f5f5f5", 
                borderRadius: "8px",
                marginBottom: "10px",
                display: "flex",
                alignItems: "center",
                gap: 1
              }}>
                <Typography variant="body2" color="text.secondary">
                  Showing {tableData.length} result{tableData.length !== 1 ? 's' : ''}
                  {debouncedSearchVal && ` for "${debouncedSearchVal}"`}
                  {searchStatus !== 3 && ` (${searchStatus === 2 ? 'Not Evaluated' : searchStatus === 1 ? 'Approved' : 'Rejected'})`}
                </Typography>
              </Box>
            )}
            <DataTable
              title="Participant Requirements"
              fields={["Event Title", "Participant Name", "Status", "Actions"]}
              data={tableData}
              onSearch={(key) => setSearchVal(key)}
              componentBeforeSearch={ModRightComponents}
              // componentOnLeft={ModLeftComponents}
            />
          </>
        )}
      </PageLayout>
    </>
  );
};

export default RequirementEvalPage;
