import React, { useEffect, useMemo, useState } from "react";
import {
  Typography,
  Box,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
} from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import StackedBarChartIcon from "@mui/icons-material/StackedBarChart";
import ReportProblemIcon from "@mui/icons-material/ReportProblem";
import PanToolAltIcon from "@mui/icons-material/PanToolAlt";
import VisibilityIcon from "@mui/icons-material/Visibility";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import FlexBox from "../FlexBox";
import CurtainPanel from "../Curtain/CurtainPanel";
import { getDropoutRiskAnalytics } from "../../api/analytics";

const MAROON = "#6d2e2e";
const HIGHLIGHT_BG = "#fff8e6";
const METRIC_BORDER = "#e8dfd0";

const MAX_CAP_DAYS = 40;

type AtRiskVolunteer = {
  name?: string;
  inactivityDays?: number;
  lastEvent?: string;
  riskScore?: number;
  joinedEvents?: number;
  attendedEvents?: number;
  attendanceRate?: number;
};

function capDays(days: unknown): number {
  return Math.min(Number(days) || 0, MAX_CAP_DAYS);
}

function activityLabel(v: AtRiskVolunteer): string {
  const raw = Number(v.inactivityDays) || 0;
  const d = Math.min(raw, MAX_CAP_DAYS);
  if (raw >= MAX_CAP_DAYS || d >= MAX_CAP_DAYS) return "Inactive for 40+ days";
  if (raw >= 30) return "Inactive for 30+ days";
  if (raw >= 14) return "Inactive for 2+ weeks";
  if (raw >= 7) return "Inactive for 1+ weeks";
  return "Recently inactive";
}

function engagementLabel(v: AtRiskVolunteer): string {
  const rate = Number(v.attendanceRate);
  const attended = Number(v.attendedEvents) || 0;
  const joined = Number(v.joinedEvents) || 0;
  if (!Number.isFinite(rate) && joined === 0 && attended === 0) return "Low";
  if (Number.isFinite(rate) && rate < 50) return "Low";
  if (attended < 2 && joined > 0) return "Low";
  if (Number.isFinite(rate) && rate < 75) return "Moderate";
  return "Moderate";
}

function riskLabel(score: number): "High" | "Medium" | "Low" {
  if (score >= 70) return "High";
  if (score >= 55) return "Medium";
  return "Low";
}

const MetricCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  value: string;
  valueColor?: string;
}> = ({ icon, title, value, valueColor }) => (
  <Box
    sx={{
      flex: 1,
      minWidth: { xs: "100%", sm: "140px" },
      border: `1px solid ${METRIC_BORDER}`,
      borderRadius: "10px",
      p: 1.5,
      bgcolor: "#faf8f5",
      display: "flex",
      flexDirection: "column",
      alignItems: "flex-start",
      gap: 0.75,
    }}
  >
    <FlexBox alignItems="center" gap={0.75}>
      <Box sx={{ color: MAROON, display: "flex", "& svg": { fontSize: 22 } }}>
        {icon}
      </Box>
      <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 0.3 }}>
        {title}
      </Typography>
    </FlexBox>
    <Typography
      variant="body2"
      fontWeight={600}
      sx={{ ...(valueColor ? { color: valueColor } : {}), lineHeight: 1.35 }}
    >
      {value}
    </Typography>
  </Box>
);

const VolunteerStatusAlert: React.FC = () => {
  const [atRiskVolunteers, setAtRiskVolunteers] = useState<AtRiskVolunteer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await getDropoutRiskAnalytics("");
        if (cancelled) return;
        if (response?.success) {
          setAtRiskVolunteers(response.data?.atRiskVolunteers || []);
        } else {
          const msg = response?.error || response?.message || "Failed to load volunteer status.";
          setError(msg);
        }
      } catch (e: unknown) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load volunteer status.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const topVolunteer = useMemo(() => {
    if (!atRiskVolunteers.length) return null;
    return [...atRiskVolunteers].sort((a, b) => (b.riskScore || 0) - (a.riskScore || 0))[0];
  }, [atRiskVolunteers]);

  const hasAlert = atRiskVolunteers.length > 0 && topVolunteer;

  const risk = topVolunteer ? riskLabel(Number(topVolunteer.riskScore) || 0) : "Low";
  const riskDisplayColor = risk === "High" ? "#c62828" : risk === "Medium" ? "#ef6c00" : undefined;

  if (loading) {
    return (
      <FlexBox
        flexDirection="column"
        borderRadius="10px"
        padding="24px"
        boxShadow="0 0 10px 1px rgba(0,0,0,0.12)"
        minHeight="200px"
        minWidth={{ xs: "100%", md: "380px" }}
        flex="1"
        alignItems="center"
        justifyContent="center"
      >
        <CircularProgress size={36} sx={{ color: MAROON }} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Loading volunteer status…
        </Typography>
      </FlexBox>
    );
  }

  if (error) {
    return (
      <FlexBox
        flexDirection="column"
        borderRadius="10px"
        padding="16px"
        boxShadow="0 0 10px 1px rgba(0,0,0,0.12)"
        minWidth={{ xs: "100%", md: "380px" }}
        flex="1"
      >
        <Alert severity="warning">{error}</Alert>
      </FlexBox>
    );
  }

  if (!hasAlert) {
    return (
      <FlexBox
        flexDirection="column"
        borderRadius="10px"
        padding="20px"
        boxShadow="0 0 10px 1px rgba(0,0,0,0.12)"
        minWidth={{ xs: "100%", md: "380px" }}
        flex="1"
        sx={{ bgcolor: "#f5faf6", border: "1px solid #c8e6c9" }}
      >
        <FlexBox alignItems="center" gap={1} mb={1}>
          <CheckCircleOutlineIcon sx={{ color: "#2e7d32", fontSize: 28 }} />
          <Typography fontWeight={700} sx={{ color: "#2e7d32" }}>
            Volunteer Status
          </Typography>
        </FlexBox>
        <Typography variant="body2" color="text.secondary">
          No volunteers are currently flagged for status review. At-risk profiles appear here when dropout analytics identify them.
        </Typography>
      </FlexBox>
    );
  }

  return (
    <>
      <FlexBox
        flexDirection="column"
        borderRadius="10px"
        padding="0"
        boxShadow="0 0 10px 1px rgba(0,0,0,0.15)"
        overflow="hidden"
        minWidth={{ xs: "100%", md: "400px" }}
        maxWidth={{ lg: "520px" }}
        flex="1"
        sx={{ bgcolor: "#fff" }}
      >
        <FlexBox
          justifyContent="space-between"
          alignItems="center"
          sx={{
            px: 2,
            py: 1.25,
            borderBottom: "1px solid #eee",
            bgcolor: "#fffdfb",
          }}
        >
          <FlexBox alignItems="center" gap={1}>
            <WarningAmberIcon sx={{ color: "#f9a825", fontSize: 28 }} />
            <Typography fontWeight={800} sx={{ color: MAROON, fontSize: "1.05rem" }}>
              Volunteer Status Alert
            </Typography>
          </FlexBox>
          <Button
            variant="outlined"
            size="small"
            startIcon={<VisibilityIcon sx={{ fontSize: 18 }} />}
            onClick={() => setDetailsOpen(true)}
            sx={{
              textTransform: "none",
              fontWeight: 700,
              borderColor: MAROON,
              color: MAROON,
              "&:hover": { borderColor: MAROON, bgcolor: "rgba(109,46,46,0.06)" },
            }}
          >
            VIEW DETAILS
          </Button>
        </FlexBox>

        <Box sx={{ px: 2, py: 1.5 }}>
          <Box
            sx={{
              bgcolor: HIGHLIGHT_BG,
              border: "1px solid #ffe082",
              borderRadius: "8px",
              px: 1.5,
              py: 1,
              mb: 1.5,
            }}
          >
            <Typography variant="body2" sx={{ color: "#5d4037" }}>
              This volunteer requires attention due to <strong>recent activity patterns</strong>.
              {topVolunteer?.name ? (
                <>
                  {" "}
                  <Typography component="span" variant="body2" fontWeight={700}>
                    ({topVolunteer.name})
                  </Typography>
                </>
              ) : null}
            </Typography>
          </Box>

          <FlexBox gap={1.5} flexWrap="wrap" mb={1.5}>
            <MetricCard
              icon={<AccessTimeIcon />}
              title="Activity status"
              value={activityLabel(topVolunteer!)}
            />
            <MetricCard
              icon={<StackedBarChartIcon />}
              title="Engagement level"
              value={engagementLabel(topVolunteer!)}
            />
            <MetricCard
              icon={<ReportProblemIcon />}
              title="Risk level"
              value={risk}
              valueColor={riskDisplayColor}
            />
          </FlexBox>

          <FlexBox
            alignItems="flex-start"
            gap={1}
            sx={{
              mt: 0.5,
              pt: 1.5,
              borderTop: "1px solid #eee",
            }}
          >
            <PanToolAltIcon sx={{ color: MAROON, fontSize: 20, mt: 0.25 }} />
            <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.5 }}>
              <strong style={{ color: MAROON }}>Review volunteer status</strong> and consider reaching out to improve engagement.
            </Typography>
          </FlexBox>
        </Box>
      </FlexBox>

      <CurtainPanel
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        title="Volunteer Status Alert — Flagged volunteers"
        direction="down"
        maxHeight="70vh"
        maxWidth="520px"
      >
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Based on the same dropout analytics as the dashboard: volunteers with risk score ≥ 50, sorted by priority.
        </Typography>
        <List dense sx={{ maxHeight: 320, overflow: "auto" }}>
          {atRiskVolunteers
            .slice()
            .sort((a, b) => (b.riskScore || 0) - (a.riskScore || 0))
            .map((volunteer, index) => (
              <ListItem key={`${volunteer.name}-${index}`} sx={{ px: 0, alignItems: "flex-start" }}>
                <ListItemText
                  primary={
                    <Typography variant="body2" fontWeight={700}>
                      {volunteer.name}
                    </Typography>
                  }
                  secondary={
                    <FlexBox gap={0.5} flexWrap="wrap" mt={0.5}>
                      <Chip
                        size="small"
                        label={`Risk: ${riskLabel(Number(volunteer.riskScore) || 0)}`}
                        color={
                          (volunteer.riskScore || 0) >= 70 ? "error" : (volunteer.riskScore || 0) >= 55 ? "warning" : "default"
                        }
                        sx={{ height: 22, fontSize: "0.7rem" }}
                      />
                      <Chip
                        size="small"
                        variant="outlined"
                        label={`${capDays(volunteer.inactivityDays)}+ days inactive`}
                        sx={{ height: 22, fontSize: "0.7rem" }}
                      />
                      <Typography variant="caption" display="block" width="100%" sx={{ mt: 0.5 }}>
                        Last event: {volunteer.lastEvent ?? "—"}
                      </Typography>
                    </FlexBox>
                  }
                />
              </ListItem>
            ))}
        </List>
      </CurtainPanel>
    </>
  );
};

export default VolunteerStatusAlert;
