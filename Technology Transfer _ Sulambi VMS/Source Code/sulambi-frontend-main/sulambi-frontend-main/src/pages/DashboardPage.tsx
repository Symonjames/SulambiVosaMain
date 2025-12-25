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
import GroupAddIcon from "@mui/icons-material/GroupAdd";
import { useEffect, useState } from "react";
import { getDashboardAnalytics, getDashboardSummary } from "../api/dashboard";
// REMOVED: clearAnalyticsData import - was deleting data on every page load
import {
 
  DashboardDataType,
  ExternalEventProposalType,
  InternalEventProposalType,
} from "../interface/types";
import { BarChart } from "@mui/x-charts";
import { Box, Typography } from "@mui/material";
import SelectionCard from "../components/Cards/SelectionCard";
import { getAllEvents } from "../api/events";
import EventDetail from "../components/Popups/EventDetail";
import ActiveMembersDashboard from "../components/Popups/ActiveMembersDashboard";
import { getAllReports } from "../api/reports";
import { useNavigate } from "react-router-dom";
import PredictiveSatisfactionRatings from "../components/Analytics/PredictiveSatisfactionRatings";
import DropoutRiskAssessment from "../components/Analytics/DropoutRiskAssessment";
import FloatingCalendarButton from "../components/FloatingCalendar/FloatingCalendarButton";
import ProjectSearchBar from "../components/Search/ProjectSearchBar";

const iconSx = {
  height: "45px",
  width: "45px",
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

  // Debug: Log state changes
  useEffect(() => {
    console.log('[DASHBOARD STATE] ageGroupData:', ageGroupData);
    console.log('[DASHBOARD STATE] sexGroupData:', sexGroupData);
    console.log('[DASHBOARD STATE] ageGroupData length:', ageGroupData.length);
    console.log('[DASHBOARD STATE] sexGroupData length:', sexGroupData.length);
  }, [ageGroupData, sexGroupData]);

  const [events, setEvents] = useState<
    (ExternalEventProposalType | InternalEventProposalType)[]
  >([]);

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

  const accountType = localStorage.getItem("accountType");
  
  // REMOVED: Auto-clear analytics data - this was deleting the data on every page load
  // The data should persist and display in analytics widgets

  useEffect(() => {
    getDashboardSummary().then((response) => {
      const data = response.data.data || {};
      console.log('[DASHBOARD] Summary data received:', data);
      setDashboardData({
        implementedEvent: data.implementedEvent || 0,
        pendingEvents: data.pendingEvents || 0,
        rejectedEvents: data.rejectedEvents || 0,
        totalAccounts: data.totalAccounts || 0,
        totalActiveMembers: data.totalActiveMembers || 0,
        totalApprovedEvents: data.totalApprovedEvents || 0,
        totalMembers: data.totalMembers || 0,
        totalPendingMembers: data.totalPendingMembers || 0,
        totalAllMembers: data.totalAllMembers || 0, // Total members uploaded (all statuses)
      });
      console.log('[DASHBOARD] Member counts:', {
        totalAllMembers: data.totalAllMembers || 0,
        totalPendingMembers: data.totalPendingMembers || 0,
        totalMembers: data.totalMembers || 0,
        totalActiveMembers: data.totalActiveMembers || 0,
      });
    }).catch((error) => {
      console.error('Error fetching dashboard summary:', error);
    });

        getDashboardAnalytics().then((response) => {
      // Debug: Log the full response structure
      console.log('[DASHBOARD] Full API response:', response);
      console.log('[DASHBOARD] response.data:', response.data);
      console.log('[DASHBOARD] response.data.data:', response.data?.data);
      
      // Only process if response has valid data structure
      if (!response?.data?.data) {
        console.log('[DASHBOARD] No API data available - response structure:', {
          hasResponse: !!response,
          hasData: !!response?.data,
          hasDataData: !!response?.data?.data,
          responseKeys: response?.data ? Object.keys(response.data) : []
        });
        setAgeGroupData([]);
        setSexGroupData([]);
        return;
      }

      const sexGroup = response.data.data.sexGroup || {};
      const ageGroup = response.data.data.ageGroup || {};
      
      // Debug: Log the raw API response to see what we're getting
      console.log('[DASHBOARD] Raw analytics API response:', {
        sexGroup,
        ageGroup,
        totalSexEntries: Object.keys(sexGroup).length,
        totalAgeEntries: Object.keys(ageGroup).length,
        sexGroupType: typeof sexGroup,
        ageGroupType: typeof ageGroup,
        sexGroupKeys: Object.keys(sexGroup),
        ageGroupKeys: Object.keys(ageGroup),
        sexGroupValues: Object.values(sexGroup),
        ageGroupValues: Object.values(ageGroup)
      });
      
      // Log the actual structure
      console.log('[DASHBOARD] sexGroup object:', JSON.stringify(sexGroup, null, 2));
      console.log('[DASHBOARD] ageGroup object:', JSON.stringify(ageGroup, null, 2));
      
      // Check if data is actually empty
      if (Object.keys(sexGroup).length === 0 && Object.keys(ageGroup).length === 0) {
        console.error('[DASHBOARD] ERROR: Both sexGroup and ageGroup are empty!');
        console.error('[DASHBOARD] Full response structure:', JSON.stringify(response.data, null, 2));
      }

      // Validate and sanitize sex group data - only include if total > 0
      console.log('[DASHBOARD] Processing sexGroup, keys:', Object.keys(sexGroup));
      const validatedSexData = Object.keys(sexGroup)
        .filter(sex => {
          const isValid = sex && sex.trim() !== '';
          console.log(`[DASHBOARD] Sex key "${sex}" is valid:`, isValid);
          return isValid;
        })
        .map((sex) => {
          const total = sexGroup[sex];
          // Convert to number if it's a string
          const totalNum = typeof total === 'string' ? parseInt(total, 10) : total;
          const processed = {
            sex: sex.trim().charAt(0).toUpperCase() + sex.trim().slice(1).toLowerCase(), // Normalize case
            total: typeof totalNum === 'number' && !isNaN(totalNum) && totalNum > 0 ? totalNum : 0       
          };
          console.log(`[DASHBOARD] Processing sex "${sex}":`, { original: sex, total, totalNum, processed });
          return processed;
        })
        .filter(item => {
          const isValid = item.total > 0;
          console.log(`[DASHBOARD] Sex item "${item.sex}" with total ${item.total} is valid:`, isValid);
          return isValid;
        })
        .sort((a, b) => a.sex.localeCompare(b.sex)); // Sort alphabetically

      // Set real data only - no fallback
      console.log('[DASHBOARD] Setting sex group data:', validatedSexData);
      setSexGroupData(validatedSexData);

      // Validate and sanitize age group data - only include if total > 0
      console.log('[DASHBOARD] Processing ageGroup, keys:', Object.keys(ageGroup));
      const validatedAgeData = Object.keys(ageGroup)
        .filter(age => {
          const isValid = age && age.toString().trim() !== '';
          console.log(`[DASHBOARD] Age key "${age}" is valid:`, isValid);
          return isValid;
        })
        .map((age) => {
          const total = ageGroup[age];
          // Convert to number if it's a string
          const totalNum = typeof total === 'string' ? parseInt(total, 10) : total;
          const ageNum = parseInt(age.toString().trim(), 10);
          const processed = {
            age: `Age ${age}`,
            ageNum: isNaN(ageNum) ? 999 : ageNum, // For sorting
            total: typeof totalNum === 'number' && !isNaN(totalNum) && totalNum > 0 ? totalNum : 0       
          };
          console.log(`[DASHBOARD] Processing age "${age}":`, { original: age, total, totalNum, ageNum, processed });
          return processed;
        })
        .filter(item => {
          const isValid = item.total > 0 && !isNaN(item.ageNum);
          console.log(`[DASHBOARD] Age item "${item.age}" with total ${item.total} is valid:`, isValid);
          return isValid;
        })
        .sort((a, b) => a.ageNum - b.ageNum) // Sort numerically by age
        .map(({ ageNum, ...rest }) => rest); // Remove ageNum after sorting

      // Set real data only - no fallback
      console.log('[DASHBOARD] Setting age group data:', validatedAgeData);
      setAgeGroupData(validatedAgeData);
    }).catch((error) => {
      console.error('Error fetching dashboard analytics:', error);
      // Show empty arrays on error - no dummy data
      setSexGroupData([]);
      setAgeGroupData([]);
    });

    getAllEvents().then((response) => {
      const externalEvent: ExternalEventProposalType[] = response.data.external || [];
      const internalEvent: InternalEventProposalType[] = response.data.internal || [];

      setEvents(
        [...externalEvent, ...internalEvent].filter(
          (event) => event && event.status === "accepted"
        )
      );
    }).catch((error) => {
      console.error('Error fetching events:', error);
      setEvents([]);
    });

    // Minimal connectivity check for reports endpoint; the grid fetches its own data
    console.log('🔍 Testing backend connectivity...');
    console.log('🔍 BASE_API_URL:', import.meta.env.VITE_API_URI);
    getAllReports()
      .then(() => console.log('🔍 Reports endpoint reachable'))
      .catch((error) => console.error('❌ Reports endpoint error:', error));
  }, []);

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
          <Box sx={{ minWidth: '320px', maxWidth: '700px', flex: 1 }}>
            <ProjectSearchBar
              onSearchResults={(results) => {
                console.log('Search results:', results);
              }}
              onYearFilter={(year) => {
                console.log('Year filter:', year);
              }}
              placeholder="Search projects, locations, or descriptions..."
              showFilters={true}
              maxWidth="100%"
            />
          </Box>
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
            value={dashboardData.totalApprovedEvents}
            label="Approved Events"
            icon={<StadiumIcon sx={iconSx} />}
            onClick={() => {
              const accountType = localStorage.getItem("accountType");
              if (accountType === "admin") {
                navigate("/admin/event-approval?status=accepted");
              } else if (accountType === "officer") {
                navigate("/officer/event-proposal?status=accepted");
              }
            }}
          />
          <DashboardCard
            value={dashboardData.pendingEvents}
            label="Pending Events"
            icon={<PendingIcon sx={iconSx} />}
            onClick={() => {
              const accountType = localStorage.getItem("accountType");
              if (accountType === "admin") {
                navigate("/admin/event-approval?status=submitted");
              } else if (accountType === "officer") {
                navigate("/officer/event-proposal?status=submitted");
              }
            }}
          />
          <DashboardCard
            value={dashboardData.rejectedEvents}
            label="Not Approved Event"
            icon={<DangerousIcon sx={iconSx} />}
            onClick={() => {
              const accountType = localStorage.getItem("accountType");
              if (accountType === "admin") {
                navigate("/admin/event-approval?status=rejected");
              } else if (accountType === "officer") {
                navigate("/officer/event-proposal?status=rejected");
              }
            }}
          />
          <DashboardCard
            value={dashboardData.implementedEvent}
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
            value={dashboardData.totalActiveMembers}
            label="Total Active Member(s)"
            icon={<GroupAddIcon sx={iconSx} />}
            onClick={
              accountType === "officer"
                ? () => {
                    navigate("/officer/membership-approval?account_status=1");
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
            events={events}
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
