import React, { useState, useEffect } from 'react';
import FlexBox from '../FlexBox';
import { Typography, Box, Chip, Alert, List, ListItem, ListItemText, CircularProgress, Button } from '@mui/material';
import { BarChart } from '@mui/x-charts';
import { CheckCircle, TrendingDown, TrendingUp, Visibility, WarningAmber, AccessTime, ReportProblem, PanToolAlt } from '@mui/icons-material';
import { getDropoutRiskAnalytics } from '../../api/analytics';
import CurtainPanel from '../Curtain/CurtainPanel';

const MAROON = "#6d2e2e";
const HIGHLIGHT_BG = "#fff8e6";
const METRIC_BORDER = "#e8dfd0";

const DropoutRiskAssessment: React.FC = () => {
  const MAX_DISPLAY_INACTIVITY_DAYS = 40;
  const capDays = (days: any) => Math.min(Number(days) || 0, MAX_DISPLAY_INACTIVITY_DAYS);
  const [semesterEngagementData, setSemesterEngagementData] = useState<any[]>([]);
  const [atRiskVolunteers, setAtRiskVolunteers] = useState<any[]>([]);
  const [averageEngagement, setAverageEngagement] = useState(0);
  const [averageInactivity, setAverageInactivity] = useState(0);
  const [riskLevel, setRiskLevel] = useState('Low');
  const [dropoutTrend, setDropoutTrend] = useState('Stable');
  const [retentionRate, setRetentionRate] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [curtainOpen, setCurtainOpen] = useState(false);

  const isAuthRelatedMessage = (msg: string) =>
    /unauthorized|log in|sign in|session expired|session invalid|403/i.test(msg || '');

  // Load real data from API
  useEffect(() => {
    const loadDropoutData = async () => {
      try {
        setLoading(true);
        setError(null);
        setIsAuthError(false);

        const response = await getDropoutRiskAnalytics('');

        if (response && response.success) {
          setSemesterEngagementData(response.data?.semesterData || []);
          setAtRiskVolunteers(response.data?.atRiskVolunteers || []);
        } else {
          const errorMsg = response?.error || response?.message || 'Failed to load dropout risk data';
          if (isAuthRelatedMessage(errorMsg)) {
            setError('Sign in to view dropout risk.');
            setIsAuthError(true);
          } else {
            setError(`Failed to load dropout risk data: ${errorMsg}`);
          }
        }
      } catch (err: any) {
        const errorMessage = err?.message || err?.toString() || 'Unknown error occurred';
        if (isAuthRelatedMessage(errorMessage)) {
          setError('Sign in to view dropout risk.');
          setIsAuthError(true);
        } else {
          setError(`Error loading dropout risk data: ${errorMessage}`);
        }
      } finally {
        setLoading(false);
      }
    };

    loadDropoutData();
  }, []);

  // Calculate metrics based on semester data
  useEffect(() => {
    if (semesterEngagementData.length > 0) {
      // Calculate average engagement across all semesters
      const totalEngagement = semesterEngagementData.reduce((sum, d) => sum + (d.events || 0), 0);
      const avgEngagement = totalEngagement / semesterEngagementData.length;
      setAverageEngagement(Number(avgEngagement.toFixed(1)));
      
      // Calculate overall retention rate from latest semester data
      const latestSemester = semesterEngagementData[semesterEngagementData.length - 1];
      if (latestSemester && latestSemester.volunteers && latestSemester.dropouts !== undefined) {
        const retention = ((latestSemester.volunteers - latestSemester.dropouts) / latestSemester.volunteers) * 100;
        setRetentionRate(Number(retention.toFixed(1)));
        
        // Determine risk level based on dropout rate
        const dropoutRate = (latestSemester.dropouts / latestSemester.volunteers) * 100;
        if (dropoutRate > 15) setRiskLevel('High');
        else if (dropoutRate > 8) setRiskLevel('Medium');
        else setRiskLevel('Low');
      }
    }

    // Calculate trend based on semester data
    if (semesterEngagementData.length >= 2) {
      const recentSemesters = semesterEngagementData.slice(-2);
      const current = recentSemesters[1];
      const previous = recentSemesters[0];
      
      if (current && previous && current.volunteers && previous.volunteers) {
        const currentDropoutRate = (current.dropouts / current.volunteers) * 100;
        const previousDropoutRate = (previous.dropouts / previous.volunteers) * 100;
        
        if (currentDropoutRate > previousDropoutRate + 2) setDropoutTrend('Increasing');
        else if (currentDropoutRate < previousDropoutRate - 2) setDropoutTrend('Decreasing');
        else setDropoutTrend('Stable');
      }
    }

    // Calculate average inactivity
    if (atRiskVolunteers.length > 0) {
      const avgInactivity = atRiskVolunteers.reduce((sum, v) => sum + v.inactivityDays, 0) / atRiskVolunteers.length;
      setAverageInactivity(Number(avgInactivity.toFixed(0)));
    }
  }, [semesterEngagementData, atRiskVolunteers]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'Increasing':
        return <TrendingUp sx={{ color: '#f44336', fontSize: 16 }} />;
      case 'Decreasing':
        return <TrendingDown sx={{ color: '#4caf50', fontSize: 16 }} />;
      default:
        return <CheckCircle sx={{ color: '#ff9800', fontSize: 16 }} />;
    }
  };

  const highInactivityCount = atRiskVolunteers.filter(
    (v) => capDays(v?.inactivityDays) >= MAX_DISPLAY_INACTIVITY_DAYS
  ).length;
  const hasHighRiskSignal = riskLevel === 'High' || highInactivityCount > 0;
  const statusLabel = hasHighRiskSignal ? 'High Risk' : `${riskLevel} Risk`;
  const conditionLabel = hasHighRiskSignal
    ? '40+ days inactive'
    : `${capDays(averageInactivity)} days inactive`;
  const riskLabel = hasHighRiskSignal
    ? '100% dropout risk (next event)'
    : `${Math.max(0, Math.round(100 - retentionRate))}% dropout risk (next event)`;

  // Summary view component
  const SummaryView = () => (
    <FlexBox
      flexDirection="column"
      borderRadius="10px"
      padding="0"
      boxShadow="0 0 10px 1px rgba(0,0,0,0.15)"
      overflow="hidden"
      flex="1"
      sx={{
        minWidth: { xs: "100%", md: "400px" },
        flex: '1 1 0',
        maxWidth: { lg: "520px" },
        bgcolor: "#fff",
      }}
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
          <WarningAmber sx={{ color: "#f9a825", fontSize: 28 }} />
          <Typography fontWeight={800} sx={{ color: MAROON, fontSize: "1.05rem" }}>
            Dropout Risk Assessment
          </Typography>
        </FlexBox>
        <Button
          variant="outlined"
          size="small"
          startIcon={<Visibility sx={{ fontSize: 18 }} />}
          onClick={() => setCurtainOpen(true)}
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
            Current volunteer retention indicates{" "}
            <strong>{hasHighRiskSignal ? "urgent attention is needed" : "stable engagement patterns"}</strong>.
          </Typography>
        </Box>

        <FlexBox gap={1.5} flexWrap="wrap" mb={1.5}>
          <Box
            sx={{
              flex: 1,
              minWidth: { xs: "100%", sm: "140px" },
              border: `1px solid ${METRIC_BORDER}`,
              borderRadius: "10px",
              p: 1.5,
              bgcolor: "#faf8f5",
            }}
          >
            <FlexBox alignItems="center" gap={0.75}>
              <AccessTime sx={{ color: MAROON, fontSize: 22 }} />
              <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 0.3 }}>
                Condition
              </Typography>
            </FlexBox>
            <Typography variant="body2" fontWeight={600} sx={{ lineHeight: 1.35, mt: 0.75 }}>
              {conditionLabel}
            </Typography>
          </Box>

          <Box
            sx={{
              flex: 1,
              minWidth: { xs: "100%", sm: "140px" },
              border: `1px solid ${METRIC_BORDER}`,
              borderRadius: "10px",
              p: 1.5,
              bgcolor: "#faf8f5",
            }}
          >
            <FlexBox alignItems="center" gap={0.75}>
              <ReportProblem sx={{ color: MAROON, fontSize: 22 }} />
              <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 0.3 }}>
                Risk level
              </Typography>
            </FlexBox>
            <Typography
              variant="body2"
              fontWeight={600}
              sx={{
                lineHeight: 1.35,
                mt: 0.75,
                color: hasHighRiskSignal ? "#c62828" : riskLevel === "Medium" ? "#ef6c00" : undefined,
              }}
            >
              {statusLabel}
            </Typography>
          </Box>
        </FlexBox>

        <Box
          sx={{
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            padding: '12px',
            backgroundColor: '#fafafa',
            mb: 1.5,
          }}
        >
          <Typography variant="body2">
            <strong>Risk Forecast:</strong> {riskLabel}
          </Typography>
        </Box>

        <FlexBox
          alignItems="flex-start"
          gap={1}
          sx={{
            mt: 0.5,
            pt: 1.5,
            borderTop: "1px solid #eee",
          }}
        >
          <PanToolAlt sx={{ color: MAROON, fontSize: 20, mt: 0.25 }} />
          <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.5 }}>
            <strong style={{ color: MAROON }}>
              {hasHighRiskSignal ? "Immediate intervention is recommended" : "Keep monitoring volunteer engagement"}
            </strong>{" "}
            to prevent future dropouts.
          </Typography>
        </FlexBox>
      </Box>
    </FlexBox>
  );

  const interpretation = [
    `Risk Level: ${riskLevel} (Retention: ${retentionRate}%)`,
    `Engagement: ${averageEngagement} events/volunteer`,
    `Average Inactivity: ${capDays(averageInactivity)} days`
  ];

  // Prediction should be "bad" when many volunteers are dropping out OR many are at max inactivity (40 days).
  // Otherwise it can be stable/good.
  const highInactivityRatio = atRiskVolunteers.length > 0 ? highInactivityCount / atRiskVolunteers.length : 0;

  // Recompute latest dropout rate (mirrors earlier logic, but keeps prediction deterministic)
  const latestSemester = semesterEngagementData.length > 0 ? semesterEngagementData[semesterEngagementData.length - 1] : null;
  const latestVolunteers = Number(latestSemester?.volunteers) || 0;
  const latestDropouts = Number(latestSemester?.dropouts) || 0;
  const latestDropoutRate = latestVolunteers > 0 ? (latestDropouts / latestVolunteers) * 100 : 0;

  type PredictionTone = "bad" | "stable" | "good";
  const predictionTone: PredictionTone =
    // "bad" signals: high dropout rate OR lots of max-inactivity volunteers
    (latestDropoutRate >= 15) ||
    (highInactivityCount >= 8) ||
    (highInactivityRatio >= 0.5)
      ? "bad"
      : // "stable" signals: moderate dropout / some at-risk
      (latestDropoutRate >= 8) ||
        (atRiskVolunteers.length >= 5) ||
        (capDays(averageInactivity) >= 20)
        ? "stable"
        : "good";

  const prediction =
    predictionTone === "bad"
      ? "Prediction: Dropout risk is high — many volunteers are inactive or dropping out. Re-engagement is recommended."
      : predictionTone === "good"
        ? "Prediction: Dropout risk looks low — attendance is healthy and inactivity is minimal."
        : `Prediction: Dropout risk is expected to remain ${dropoutTrend.toLowerCase()} next semester.`;

  const predictionBoxSx =
    predictionTone === "bad"
      ? { backgroundColor: "#fff5f5", border: "1px solid #ffcdd2" }
      : predictionTone === "good"
        ? { backgroundColor: "#f1fff4", border: "1px solid #b9f6ca" }
        : { backgroundColor: "#f4f8ff", border: "1px solid #d0e3ff" };

  if (loading) {
    return (
      <FlexBox
        flexDirection="column"
        borderRadius="10px"
        padding="16px"
        boxShadow="0 0 10px 1px gray"
        minHeight="500px"
        flex="1"
        alignItems="center"
        justifyContent="center"
        sx={{
          minWidth: '500px',
          flex: '1 1 0',
          maxWidth: 'none',
          '@media (max-width: 768px)': {
            minWidth: '100%',
            maxWidth: '100%',
          }
        }}
      >
        <CircularProgress size={40} />
        <Typography variant="body2" color="text.secondary" mt={2}>
          Loading dropout risk data...
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
        boxShadow="0 0 10px 1px gray"
        minHeight="500px"
        flex="1"
        sx={{
          minWidth: '500px',
          flex: '1 1 0',
          maxWidth: 'none',
          '@media (max-width: 768px)': {
            minWidth: '100%',
            maxWidth: '100%',
          }
        }}
      >
        <Typography textAlign="center" fontWeight="bold" gutterBottom>
          Dropout Risk Assessment
        </Typography>
        <Alert severity={isAuthError ? 'info' : 'error'} sx={{ mt: 2 }}>
          {error}
        </Alert>
      </FlexBox>
    );
  }

  return (
    <>
      <SummaryView />
      
      <CurtainPanel
        open={curtainOpen}
        onClose={() => setCurtainOpen(false)}
        title="Dropout Risk Assessment - Detailed View"
        direction="down"
        maxHeight="75vh"
        maxWidth="600px"
      >
        <FlexBox flexDirection="column" gap={3}>
          
          {/* Risk Level Alert */}
          <Alert 
            severity={riskLevel === 'High' ? 'error' : riskLevel === 'Medium' ? 'warning' : 'success'}
            icon={false}
            sx={{ mb: 2 }}
          >
            <Typography variant="body2">
              Overall Risk Level: <strong>{riskLevel}</strong> | Retention Rate: <strong>{retentionRate}%</strong>
            </Typography>
          </Alert>

          {/* Semester Overview */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Semester Overview:
            </Typography>
            <FlexBox gap={2} mb={1}>
              <Chip 
                label={`${averageEngagement} events/volunteer`} 
                color="primary" 
                size="small"
              />
              <Chip 
                label={`${retentionRate}% retention`} 
                color={retentionRate > 90 ? 'success' : retentionRate > 80 ? 'warning' : 'error'}
                size="small"
              />
              <FlexBox alignItems="center" gap={0.5}>
                {getTrendIcon(dropoutTrend)}
                <Typography variant="caption" color="text.secondary">
                  {dropoutTrend} trend
                </Typography>
              </FlexBox>
            </FlexBox>
          </Box>

          {/* Engagement Frequency Chart */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Volunteer Engagement Frequency (events per semester)
            </Typography>
            <Box height={200}>
              <BarChart
                height={200}
                dataset={semesterEngagementData}
                xAxis={[{ 
                  scaleType: "band", 
                  dataKey: "semester", 
                  label: "Semester" 
                }]}
                yAxis={[{ 
                  label: "Events Attended", 
                  min: 0, 
                  max: 5 
                }]}
                series={[
                  { 
                    dataKey: "events", 
                    label: "Events per Volunteer",
                    color: "#333333"
                  },
                  { 
                    dataKey: "volunteers", 
                    label: "Active Volunteers",
                    color: "#2196f3"
                  }
                ]}
              />
            </Box>
            <Typography variant="caption" color="text.secondary">
              Average: {averageEngagement} events per semester
            </Typography>
          </Box>

          {/* Inactivity Duration */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Average Inactivity Duration: {capDays(averageInactivity)} days
            </Typography>
            <Chip 
              label={`${capDays(averageInactivity)} days since last involvement`} 
              color={capDays(averageInactivity) > 30 ? 'error' : capDays(averageInactivity) > 15 ? 'warning' : 'success'}
              size="small"
            />
          </Box>

          {/* Flagged At-Risk Volunteers */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Flagged At-Risk Volunteers ({atRiskVolunteers.length}):
            </Typography>
            <List dense sx={{ maxHeight: 200, overflow: 'auto' }}>
              {atRiskVolunteers
                .sort((a, b) => b.riskScore - a.riskScore)
                .map((volunteer, index) => (
                <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                  <ListItemText
                    primary={
                      <FlexBox justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" fontWeight="medium">
                          {volunteer.name}
                        </Typography>
                        <Box>
                          <Chip 
                            label={`${volunteer.riskScore}% risk`} 
                            size="small" 
                            color={volunteer.riskScore > 80 ? 'error' : volunteer.riskScore > 60 ? 'warning' : 'success'}
                            sx={{ fontSize: '0.6rem', mr: 0.5 }}
                          />
                          <Chip 
                            label={`${capDays(volunteer.inactivityDays)} days`} 
                            size="small" 
                            color={capDays(volunteer.inactivityDays) > 30 ? 'error' : 'warning'}
                            sx={{ fontSize: '0.7rem' }}
                          />
                        </Box>
                      </FlexBox>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        Last event: {volunteer.lastEvent}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>

          {/* Interpretation & Prediction */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Interpretation:
            </Typography>
            {interpretation.map((line, idx) => (
              <Typography key={idx} variant="body2" color="text.secondary">
                • {line}
              </Typography>
            ))}
            <Box
              sx={{
                mt: 2,
                p: 2,
                borderRadius: '12px',
                ...predictionBoxSx,
                fontWeight: 500,
                textAlign: 'center'
              }}
            >
              {prediction}
            </Box>
          </Box>
        </FlexBox>
      </CurtainPanel>
    </>
  );
};

export default DropoutRiskAssessment;
