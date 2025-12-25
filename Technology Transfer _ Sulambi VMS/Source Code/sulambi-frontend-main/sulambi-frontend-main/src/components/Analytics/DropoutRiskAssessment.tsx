import React, { useState, useEffect } from 'react';
import FlexBox from '../FlexBox';
import { Typography, Box, Chip, Alert, List, ListItem, ListItemText, CircularProgress, Button } from '@mui/material';
import { BarChart } from '@mui/x-charts';
import { CheckCircle, TrendingDown, TrendingUp, Visibility } from '@mui/icons-material';
import { getDropoutRiskAnalytics } from '../../api/analytics';
import CurtainPanel from '../Curtain/CurtainPanel';

const DropoutRiskAssessment: React.FC = () => {
  const [semesterEngagementData, setSemesterEngagementData] = useState<any[]>([]);
  const [atRiskVolunteers, setAtRiskVolunteers] = useState<any[]>([]);
  const [averageEngagement, setAverageEngagement] = useState(0);
  const [averageInactivity, setAverageInactivity] = useState(0);
  const [riskLevel, setRiskLevel] = useState('Low');
  const [dropoutTrend, setDropoutTrend] = useState('Stable');
  const [retentionRate, setRetentionRate] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [curtainOpen, setCurtainOpen] = useState(false);

  // Load real data from API
  useEffect(() => {
    const loadDropoutData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await getDropoutRiskAnalytics('');
        
        console.log('[DROPOUT COMPONENT] Response received:', response);
        
        if (response && response.success) {
          setSemesterEngagementData(response.data?.semesterData || []);
          setAtRiskVolunteers(response.data?.atRiskVolunteers || []);
        } else {
          const errorMsg = response?.error || response?.message || 'Failed to load dropout risk data';
          console.error('[DROPOUT COMPONENT] API returned error:', errorMsg);
          setError(`Failed to load dropout risk data: ${errorMsg}`);
        }
      } catch (err: any) {
        console.error('Error loading dropout risk data:', err);
        const errorMessage = err?.message || err?.toString() || 'Unknown error occurred';
        setError(`Error loading dropout risk data: ${errorMessage}`);
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

  // Summary view component
  const SummaryView = () => (
    <FlexBox
      flexDirection="column"
      borderRadius="10px"
      padding="16px"
      boxShadow="0 0 10px 1px gray"
      minHeight="300px"
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
      <FlexBox justifyContent="space-between" alignItems="center" mb={2}>
        <Typography textAlign="center" fontWeight="bold" gutterBottom>
          Dropout Risk Assessment
        </Typography>
        <Button
          variant="outlined"
          size="small"
          startIcon={<Visibility />}
          onClick={() => setCurtainOpen(true)}
          sx={{ minWidth: '120px' }}
        >
          View Details
        </Button>
      </FlexBox>
      
      
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

      {/* Key Metrics Summary */}
      <Box mb={2}>
        <Typography variant="subtitle2" gutterBottom>
          Key Metrics:
        </Typography>
        <FlexBox gap={2} mb={1} flexWrap="wrap">
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

      {/* Mini Chart Preview */}
      <Box height={110} mb={1.5}>
        <BarChart
          height={110}
          dataset={semesterEngagementData}
          xAxis={[{ 
            scaleType: "band", 
            dataKey: "semester", 
            label: "Semester",
            tickLabelStyle: { fontSize: 11 }
          }]}
          yAxis={[{ 
            label: "Events Attended",
            min: 0, 
            max: 5,
            tickLabelStyle: { fontSize: 11 }
          }]}
          series={[
            { 
              dataKey: "events", 
              label: "Events per Volunteer",
              color: "#2f4858"
            }
          ]}
          margin={{ top: 6, right: 10, bottom: 28, left: 32 }}
        />
      </Box>

      {/* At-Risk Volunteers Preview */}
      <Box>
        <Typography variant="subtitle2" gutterBottom>
          At-Risk Volunteers ({atRiskVolunteers.length}):
        </Typography>
        {atRiskVolunteers
          .sort((a, b) => b.riskScore - a.riskScore)
          .slice(0, 3)
          .map((volunteer, index) => (
          <FlexBox key={index} justifyContent="space-between" alignItems="center" mb={0.5}>
            <Typography variant="body2" sx={{ flex: 1, fontSize: '0.875rem' }}>
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
                label={`${volunteer.inactivityDays} days`} 
                size="small" 
                color={volunteer.inactivityDays > 45 ? 'error' : 'warning'}
                sx={{ fontSize: '0.7rem' }}
              />
            </Box>
          </FlexBox>
        ))}
        {atRiskVolunteers.length > 3 && (
          <Typography variant="caption" color="text.secondary" textAlign="center">
            +{atRiskVolunteers.length - 3} more volunteers
          </Typography>
        )}
      </Box>
    </FlexBox>
  );

  const interpretation = [
    `Risk Level: ${riskLevel} (Retention: ${retentionRate}%)`,
    `Engagement: ${averageEngagement} events/volunteer`,
    `Average Inactivity: ${averageInactivity} days`
  ];
  const prediction = `Prediction: Dropout risk is expected to remain ${dropoutTrend.toLowerCase()} next semester.`;

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
        <Alert severity="error" sx={{ mt: 2 }}>
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
              Average Inactivity Duration: {averageInactivity} days
            </Typography>
            <Chip 
              label={`${averageInactivity} days since last involvement`} 
              color={averageInactivity > 30 ? 'error' : averageInactivity > 15 ? 'warning' : 'success'}
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
                            label={`${volunteer.inactivityDays} days`} 
                            size="small" 
                            color={volunteer.inactivityDays > 45 ? 'error' : 'warning'}
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
                backgroundColor: '#f4f8ff',
                border: '1px solid #d0e3ff',
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
