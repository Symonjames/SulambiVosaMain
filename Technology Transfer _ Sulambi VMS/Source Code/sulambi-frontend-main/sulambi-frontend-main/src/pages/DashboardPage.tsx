import DashboardCard from "../components/Cards/DashboardCard";
import FlexBox from "../components/FlexBox";
import TextHeader from "../components/Headers/TextHeader";
import TextSubHeader from "../components/Headers/TextSubHeader";
import PageLayout from "./PageLayout";

import StadiumIcon from "@mui/icons-material/Stadium";
import PendingIcon from "@mui/icons-material/Pending";
import DangerousIcon from "@mui/icons-material/Dangerous";
import FactCheckIcon from "@mui/icons-material/FactCheck";
import SummarizeIcon from "@mui/icons-material/Summarize";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";
import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { AccountDetailsContext } from "../contexts/AccountDetailsProvider";
import { getDashboardAnalytics, getDashboardSummary } from "../api/dashboard";
// REMOVED: clearAnalyticsData import - was deleting data on every page load
import {
 
  DashboardDataType,
  ExternalEventProposalType,
  InternalEventProposalType,
} from "../interface/types";
import { BarChart } from "@mui/x-charts";
import { Box, Typography } from "@mui/material";
import CustomDropdown from "../components/Inputs/CustomDropdown";
import SelectionCard from "../components/Cards/SelectionCard";
import { getAllEvents } from "../api/events";
import EventDetail from "../components/Popups/EventDetail";
import ActiveMembersDashboard from "../components/Popups/ActiveMembersDashboard";
import { useNavigate } from "react-router-dom";
import PredictiveSatisfactionRatings from "../components/Analytics/PredictiveSatisfactionRatings";
import DropoutRiskAssessment from "../components/Analytics/DropoutRiskAssessment";
import VolunteerStatusAlert from "../components/Analytics/VolunteerStatusAlert";
import FloatingCalendarButton from "../components/FloatingCalendar/FloatingCalendarButton";
import ProjectSearchBar from "../components/Search/ProjectSearchBar";
import { useCachedFetch } from "../hooks/useCachedFetch";
import { CACHE_TIMES } from "../utils/apiCache";

const iconSx = {
  height: "45px",
  width: "45px",
};

const toEventMs = (value: unknown): number | null => {
  if (value == null) return null;

  if (typeof value === "number" && Number.isFinite(value)) {
    return value >= 1e12 ? value : value * 1000;
  }

  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return null;

    const asNum = Number(trimmed);
    if (Number.isFinite(asNum) && trimmed !== "") {
      return asNum >= 1e12 ? asNum : asNum * 1000;
    }

    const parsed = Date.parse(trimmed);
    return Number.isNaN(parsed) ? null : parsed;
  }

  return null;
};

const getEventYear = (value: unknown): number | null => {
  const ms = toEventMs(value);
  if (ms == null) return null;
  const year = new Date(ms).getFullYear();
  return Number.isNaN(year) ? null : year;
};

// Analytics Box Component
const AnalyticsBox : React.FC<{
  title: string;
  data: any[];
  dataKey: string;
  labelKey: string;
  height?: number;
  width?: number;
}> = ({ title, data, dataKey, labelKey, height = 180 }) => {
  const hasData = data && data.length > 0;
  
  return (
    <FlexBox
      flexDirection="column"
      borderRadius="10px"
      padding="12px"
      boxShadow="0 0 10px 1px gray"
      minHeight="220px"
      flex="1"
      sx={{
        minWidth: '200px',
        flex: '1 1 0',
        maxWidth: 'none',
        '@media (max-width: 768px)': {
          minWidth: '100%',
          maxWidth: '100%',
        }
      }}
    >
      <Typography textAlign="center" fontWeight="bold" gutterBottom fontSize="0.95rem">
        {title}
      </Typography>
      {hasData ? (
        <FlexBox
          alignItems="center"
          justifyContent="center"
          height="100%"
          sx={{ minHeight: `${height}px`, width: '100%' }}
        >
          <BarChart
            height={height}
            dataset={data}
            xAxis={[{ scaleType: "band", dataKey: labelKey, label: labelKey }]}
            yAxis={[{ label: "Number of Volunteer(s)" }]}
            series={[{ dataKey: dataKey, color: "#C07F00" }]}
          />
        </FlexBox>
      ) : (
        <FlexBox
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          height="180px"
          sx={{ color: 'text.secondary' }}
        >
          <Typography variant="h6" color="text.secondary" fontSize="0.9rem">
            No Data Available
          </Typography>
          <Typography variant="body2" color="text.secondary" fontSize="0.75rem">
            Analytics will appear here once volunteers register
          </Typography>
        </FlexBox>
      )}
    </FlexBox>
  );
};

// Events Box Component - Matching AnalyticsBox styling
const EventsBox: React.FC<{
  events: (ExternalEventProposalType | InternalEventProposalType)[];
  onEventClick: (event: ExternalEventProposalType | InternalEventProposalType) => void;
}> = ({ events, onEventClick }) => {
  const hasEvents = events && events.length > 0;
  
  return (
    <FlexBox
      flexDirection="column"
      borderRadius="10px"
      padding="16px"
      boxShadow="0 0 10px 1px gray"
      minHeight="240px"
      flex="1"
      sx={{
        minWidth: '280px',
        flex: '1 1 0',
        maxWidth: 'none',
        '@media (max-width: 768px)': {
          minWidth: '100%',
          maxWidth: '100%',
        }
      }}
    >
      <Typography textAlign="center" fontWeight="bold" gutterBottom>
        Events
      </Typography>
      {hasEvents ? (
        <Box
          width="100%"
          height="300px"
          sx={{
            overflowY: "auto",
            overflowX: "clip",
            padding: "8px",
          }}
        >
          {events.map((evt, index) => (
            <SelectionCard
              key={evt.id || index}
              enableMarginTop={index > 0}
              hideActions
              textAlign="center"
              header={evt.title}
              onClickable={() => onEventClick(evt)}
            />
          ))}
        </Box>
      ) : (
        <FlexBox
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          height="300px"
          sx={{ color: 'text.secondary' }}
        >
          <Typography variant="h6" color="text.secondary">
            No Events Available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Reports will appear here once submitted
          </Typography>
        </FlexBox>
      )}
    </FlexBox>
  );
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [openEventDetail, setOpenEventDetail] = useState(false);
  const [openMemberDetails, setOpenMemberDetails] = useState(false);
  const [eventId, setEventId] = useState(0);
  const [eventType, setEventType] = useState<"external" | "internal">(
    "external"
  );

  const [ageGroupData, setAgeGroupData] = useState<
    { age: any; total: number }[]
  >([]);

  const [sexGroupData, setSexGroupData] = useState<
    { sex: string; total: number }[]
  >([]);

  const [eventYearFilter, setEventYearFilter] = useState<string>("");

  // Photos grid now fetches its own data


  const [dashboardData, setDashboardData] = useState<DashboardDataType>({
    implementedEvent: 0,
    pendingEvents: 0,
    rejectedEvents: 0,
    totalAccounts: 0,
    totalActiveMembers: 0,
    totalApprovedEvents: 0,
    totalMembers: 0,
    totalPendingMembers: 0,
    totalAllMembers: 0, // Total members uploaded (all statuses)
  });

  const { accountDetails } = useContext(AccountDetailsContext);
  const accountType = accountDetails.accountType;

  // REMOVED: Auto-clear analytics data - this was deleting the data on every page load
  // The data should persist and display in analytics widgets

  // Use cached fetch for dashboard summary - data persists when navigating away and coming back!
  const { data: summaryResponse } = useCachedFetch({
    cacheKey: 'dashboard_summary',
    fetchFn: () => getDashboardSummary(),
    cacheTime: CACHE_TIMES.MEDIUM, // 5 minutes keeps navigation fast while staying fresh
    useMemoryCache: true,
  });

  // Use cached fetch for dashboard analytics - data persists when navigating away and coming back!
  const { data: analyticsResponse, error: analyticsError } = useCachedFetch({
    cacheKey: 'dashboard_analytics',
    fetchFn: () => getDashboardAnalytics(),
    cacheTime: CACHE_TIMES.MEDIUM, // 5 minutes keeps navigation fast while staying fresh
    useMemoryCache: true,
  });

  // Use cached fetch for events - data persists when navigating away and coming back!
  const { data: eventsResponse } = useCachedFetch({
    cacheKey: 'dashboard_events',
    fetchFn: () => getAllEvents(),
    cacheTime: CACHE_TIMES.MEDIUM, // Cache for 5 minutes
    useMemoryCache: true,
  });

  // Process dashboard summary data
  useEffect(() => {
    if (summaryResponse?.data) {
      const data = summaryResponse.data || {};
      setDashboardData({
        implementedEvent: data.implementedEvent || 0,
        pendingEvents: data.pendingEvents || 0,
        rejectedEvents: data.rejectedEvents || 0,
        totalAccounts: data.totalAccounts || 0,
        totalActiveMembers: data.totalActiveMembers || 0,
        totalApprovedEvents: data.totalApprovedEvents || 0,
        totalMembers: data.totalMembers || 0,
        totalPendingMembers: data.totalPendingMembers || 0,
        totalAllMembers: data.totalAllMembers || 0,
      });
    }
  }, [summaryResponse]);

  // Process analytics data
  useEffect(() => {
    if (analyticsError) {
      setAgeGroupData([]);
      setSexGroupData([]);
      return;
    }

    if (!analyticsResponse) {
      return;
    }

    // Handle both response.data.data and response.data structures
    const analyticsData = analyticsResponse?.data?.data || analyticsResponse?.data || {};
    
    if (!analyticsData || (Object.keys(analyticsData).length === 0 && !analyticsData.sexGroup && !analyticsData.ageGroup)) {
      setAgeGroupData([]);
      setSexGroupData([]);
      return;
    }

    const sexGroup = analyticsData.sexGroup || {};
    const ageGroup = analyticsData.ageGroup || {};
    // Validate and sanitize sex group data
    const validatedSexData = Object.keys(sexGroup)
      .filter(sex => sex && sex.trim() !== '')
      .map((sex) => {
        const total = sexGroup[sex];
        const totalNum = typeof total === 'string' ? parseInt(total, 10) : total;
        return {
          sex: sex.trim().charAt(0).toUpperCase() + sex.trim().slice(1).toLowerCase(),
          total: typeof totalNum === 'number' && !isNaN(totalNum) && totalNum > 0 ? totalNum : 0
        };
      })
      .filter(item => item.total > 0)
      .sort((a, b) => a.sex.localeCompare(b.sex));

    setSexGroupData(validatedSexData);

    // Validate and sanitize age group data
    const validatedAgeData = Object.keys(ageGroup)
      .filter(age => age && age.toString().trim() !== '')
      .map((age) => {
        const total = ageGroup[age];
        const totalNum = typeof total === 'string' ? parseInt(total, 10) : total;
        const ageNum = parseInt(age.toString().trim(), 10);
        return {
          age: `Age ${age}`,
          ageNum: isNaN(ageNum) ? 999 : ageNum,
          total: typeof totalNum === 'number' && !isNaN(totalNum) && totalNum > 0 ? totalNum : 0
        };
      })
      .filter(item => item.total > 0 && !isNaN(item.ageNum) && item.ageNum !== 12)
      .sort((a, b) => a.ageNum - b.ageNum)
      .map(({ ageNum, ...rest }) => rest);

    setAgeGroupData(validatedAgeData);
  }, [analyticsResponse, analyticsError]);

  const allEvents = useMemo(
    () =>
      eventsResponse
        ? [
            ...((eventsResponse.external || []) as ExternalEventProposalType[]),
            ...((eventsResponse.internal || []) as InternalEventProposalType[]),
          ]
        : [],
    [eventsResponse]
  );

  const events = useMemo(
    () => allEvents.filter((event) => event && event.status === "accepted"),
    [allEvents]
  );

  // Unique years from events (by start date) for the year filter
  const eventYears = useMemo(() => {
    const years = new Set<number>();
    events.forEach((evt) => {
      const y = getEventYear(evt.durationStart);
      if (y !== null) years.add(y);
    });
    return Array.from(years).sort((a, b) => b - a);
  }, [events]);

  // Events filtered by selected year (start year)
  const eventsFilteredByYear = useMemo(() => {
    if (!eventYearFilter || eventYearFilter === "all") return events;
    const yearNum = parseInt(eventYearFilter, 10);
    if (isNaN(yearNum)) return events;
    return events.filter((evt) => getEventYear(evt.durationStart) === yearNum);
  }, [events, eventYearFilter]);

  // Apply year filter to event-stat cards without changing membership/account totals.
  const displayedDashboardData = useMemo(() => {
    if (!eventYearFilter || eventYearFilter === "all") return dashboardData;
    const yearNum = parseInt(eventYearFilter, 10);
    if (isNaN(yearNum)) return dashboardData;

    const nowMs = Date.now();
    let approved = 0;
    let pending = 0;
    let rejected = 0;
    let implemented = 0;

    allEvents.forEach((event) => {
      if (!event || event.status === "editing") return;
      if (getEventYear(event.durationStart) !== yearNum) return;

      if (event.status === "accepted") {
        approved += 1;
        const endMs = toEventMs(event.durationEnd);
        if (endMs !== null && endMs < nowMs) {
          implemented += 1;
        }
      } else if (event.status === "submitted") {
        pending += 1;
      } else {
        rejected += 1;
      }
    });

    return {
      ...dashboardData,
      totalApprovedEvents: approved,
      pendingEvents: pending,
      rejectedEvents: rejected,
      implementedEvent: implemented,
    };
  }, [dashboardData, eventYearFilter, allEvents]);

  const handleProjectSearchResults = useCallback(
    (_results: (ExternalEventProposalType | InternalEventProposalType)[]) => {
      // Searchbar currently drives its own UI; keep callback stable for performance.
    },
    []
  );

  const handleProjectYearFilter = useCallback((_year: string) => {
    // Dashboard year filtering is controlled by the dropdown above.
  }, []);

  const handleProjectEventClick = useCallback(
    (event: ExternalEventProposalType | InternalEventProposalType) => {
      setEventId(event.id);
      if ((event as ExternalEventProposalType).location) {
        setEventType("external");
      } else if ((event as InternalEventProposalType).venue) {
        setEventType("internal");
      }
      setOpenEventDetail(true);
    },
    []
  );

  return (
    <>
      <EventDetail
        eventId={eventId}
        eventType={eventType}
        open={openEventDetail}
        setOpen={setOpenEventDetail}
      />
      <ActiveMembersDashboard
        open={openMemberDetails}
        setOpen={setOpenMemberDetails}
      />
      <PageLayout page="dashboard">
        {/* Header with title on the left and search+filters on the right */}
        <FlexBox
          width="100%"
          alignItems="center"
          justifyContent="space-between"
          flexWrap="wrap"
          rowGap="10px"
        >
          <Box>
            <TextHeader>DASHBOARD</TextHeader>
            <TextSubHeader>View your analytics here</TextSubHeader>
          </Box>
          <FlexBox gap="10px" alignItems="center" sx={{ marginLeft: "auto", flexWrap: "wrap" }}>
            <CustomDropdown
              label="Year"
              width="120px"
              initialValue={eventYearFilter || "all"}
              menu={[
                { key: "All years", value: "all" },
                ...eventYears.map((y) => ({ key: String(y), value: String(y) })),
              ]}
              onChange={(e) => setEventYearFilter(e.target.value === "all" ? "" : e.target.value)}
            />
            <Box sx={{ width: "320px", maxWidth: "320px" }}>
              <ProjectSearchBar
                onSearchResults={handleProjectSearchResults}
                onYearFilter={handleProjectYearFilter}
                onEventClick={handleProjectEventClick}
                placeholder="Search projects, locations, or descriptions..."
                showFilters={false}
                maxWidth="100%"
              />
            </Box>
          </FlexBox>
        </FlexBox>
        <FlexBox
          width="100%"
          rowGap="12px"
          columnGap="12px"
          flexWrap="wrap"
          marginTop="20px"
          justifyContent="flex-start"
        >
          <DashboardCard
            value={displayedDashboardData.totalApprovedEvents}
            label="Approved Events"
            icon={<StadiumIcon sx={iconSx} />}
            onClick={() => {
              if (accountType === "admin") {
                navigate("/admin/event-approval?status=accepted");
              } else if (accountType === "officer") {
                navigate("/officer/event-proposal?status=accepted");
              }
            }}
          />
          <DashboardCard
            value={displayedDashboardData.pendingEvents}
            label="Pending Events"
            icon={<PendingIcon sx={iconSx} />}
            onClick={() => {
              if (accountType === "admin") {
                navigate("/admin/event-approval?status=submitted");
              } else if (accountType === "officer") {
                navigate("/officer/event-proposal?status=submitted");
              }
            }}
          />
          <DashboardCard
            value={displayedDashboardData.rejectedEvents}
            label="Not Approved Event"
            icon={<DangerousIcon sx={iconSx} />}
            onClick={() => {
              if (accountType === "admin") {
                navigate("/admin/event-approval?status=rejected");
              } else if (accountType === "officer") {
                navigate("/officer/event-proposal?status=rejected");
              }
            }}
          />
          <DashboardCard
            value={displayedDashboardData.implementedEvent}
            label="Implemented Event"
            icon={<FactCheckIcon sx={iconSx} />}
            // onClick={() => {
            //   const accountType = localStorage.getItem("accountType");
            //   if (accountType === "admin") {
            //     navigate("/officer/event-proposal");
            //   } else if (accountType === "officer") {
            //     navigate("/admin/event-approval");
            //   }
            // }}
          />
          <DashboardCard
            value={dashboardData.totalAccounts}
            label="Total Accounts"
            icon={<SummarizeIcon sx={iconSx} />}
            onClick={
              // clickable only for admin
              accountType === "admin"
                ? () => {
                    navigate("/admin/accounts");
                  }
                : undefined
            }
          />
          <DashboardCard
            value={dashboardData.totalPendingMembers}
            label="Total Pending Membership"
            icon={<SummarizeIcon sx={iconSx} />}
            onClick={
              accountType === "officer"
                ? () => {
                    navigate("/officer/membership-approval?status=2");
                  }
                : undefined
            }
          />
          <DashboardCard
            value={dashboardData.totalMembers}
            label="Total Member(s)"
            icon={<PeopleAltIcon sx={iconSx} />}
            onClick={
              accountType === "officer"
                ? () => {
                    navigate("/officer/membership-approval?status=1");
                  }
                : undefined
            }
          />
          <DashboardCard
            value={dashboardData.totalAllMembers}
            label="Total All Members (All Statuses)"
            icon={<PeopleAltIcon sx={iconSx} />}
            onClick={
              accountType === "officer"
                ? () => {
                    navigate("/officer/membership-approval");
                  }
                : undefined
            }
          />
        </FlexBox>
        {/* Search moved to header */}

        {/* Enhanced Analytics Section */}
        {/* Predictive Analytics Row - Admin only */}
        {accountType !== 'officer' && (
          <FlexBox 
            marginTop="16px" 
            gap="12px"
            justifyContent="flex-start"
            flexWrap="wrap"
            sx={{
              '@media (max-width: 1200px)': {
                flexDirection: 'column',
                gap: '12px',
              }
            }}
          >
            <PredictiveSatisfactionRatings />
            <VolunteerStatusAlert />
            <DropoutRiskAssessment />
          </FlexBox>
        )}

        {/* Traditional Analytics Row - Available for both Admin and Officer */}
        <FlexBox 
          marginTop="12px" 
          gap="12px"
          justifyContent="flex-start"
          flexWrap="wrap"
          sx={{
            '@media (max-width: 768px)': {
              flexDirection: 'column',
              gap: '10px',
            }
          }}
        >
          <AnalyticsBox
            title="Volunteer(s) Age Analytics"
            data={ageGroupData}
            dataKey="total"
            labelKey="age"
            height={180}
            width={180}
          />
          <AnalyticsBox
            title="Volunteer(s) Sex Analytics"
            data={sexGroupData}
            dataKey="total"
            labelKey="sex"
            height={180}
            width={180}
          />
          <EventsBox
            events={eventsFilteredByYear}
            onEventClick={(evt) => {
              setEventId(evt.id);
              if ((evt as ExternalEventProposalType).location)
                setEventType("external");
              if ((evt as InternalEventProposalType).venue)
                setEventType("internal");
              setOpenEventDetail(true);
            }}
          />
        </FlexBox>

        {/* Recent Photo Submissions removed per request */}

        {/* Floating Calendar Button */}
        <FloatingCalendarButton />

      </PageLayout>
    </>
  );
};

export default Dashboard;
