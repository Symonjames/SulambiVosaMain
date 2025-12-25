import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  TrendingUp,
  People,
  Star,
  Assessment,
  Timeline,
  Insights
} from '@mui/icons-material';
import PageLayout from '../PageLayout';
import TextHeader from '../../components/Headers/TextHeader';
import TextSubHeader from '../../components/Headers/TextSubHeader';
import FlexBox from '../../components/FlexBox';
import PredictiveSatisfactionRatings from '../../components/Analytics/PredictiveSatisfactionRatings';
import DropoutRiskAssessment from '../../components/Analytics/DropoutRiskAssessment';
import EventSuccessRates from '../../components/Analytics/EventSuccessRates';
import VolunteerDropoutRisk from '../../components/Analytics/VolunteerDropoutRisk';
import { getAllAnalytics } from '../../api/analytics';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AnalyticsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const currentYear = new Date().getFullYear().toString();
  const [selectedYear, setSelectedYear] = useState(currentYear);

  useEffect(() => {
    const loadAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await getAllAnalytics();
        
        if (response.success) {
          setAnalyticsData(response.data);
        } else {
          setError('Failed to load analytics data');
        }
      } catch (err) {
        console.error('Error loading analytics data:', err);
        setError('Error loading analytics data');
      } finally {
        setLoading(false);
      }
    };

    loadAnalyticsData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <PageLayout page="analytics">
        <FlexBox
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="60vh"
        >
          <CircularProgress size={60} />
          <Typography variant="h6" color="text.secondary" mt={2}>
            Loading Analytics Data...
          </Typography>
        </FlexBox>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout page="analytics">
        <TextHeader>Analytics Dashboard</TextHeader>
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      </PageLayout>
    );
  }

  return (
    <PageLayout page="analytics">
      <TextHeader>Analytics Dashboard</TextHeader>
      <TextSubHeader gutterBottom>
        Real-time analytics and insights from QR evaluations and system data
      </TextSubHeader>

      {/* Year Filter */}
      <Box mb={3}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Filter by Year</InputLabel>
          <Select
            value={selectedYear}
            label="Filter by Year"
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            {(() => {
              const currentYearNum = new Date().getFullYear();
              const years = [];
              // Generate years from 2025 to current year
              for (let year = 2025; year <= currentYearNum; year++) {
                years.push(
                  <MenuItem key={year} value={year.toString()}>
                    {year}
                  </MenuItem>
                );
              }
              return years;
            })()}
            <MenuItem value="all">All Years</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Analytics Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <FlexBox alignItems="center" gap={2}>
                <Star sx={{ fontSize: 40, color: '#4caf50' }} />
                <Box>
                  <Typography variant="h4" component="div">
                    {analyticsData?.satisfaction?.data?.averageScore || '0.0'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Average Satisfaction
                  </Typography>
                </Box>
              </FlexBox>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <FlexBox alignItems="center" gap={2}>
                <People sx={{ fontSize: 40, color: '#2196f3' }} />
                <Box>
                  <Typography variant="h4" component="div">
                    {analyticsData?.satisfaction?.data?.processedEvaluations || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    QR Evaluations
                  </Typography>
                </Box>
              </FlexBox>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <FlexBox alignItems="center" gap={2}>
                <Assessment sx={{ fontSize: 40, color: '#ff9800' }} />
                <Box>
                  <Typography variant="h4" component="div">
                    {analyticsData?.eventSuccess?.data?.completed || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Completed Events
                  </Typography>
                </Box>
              </FlexBox>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <FlexBox alignItems="center" gap={2}>
                <TrendingUp sx={{ fontSize: 40, color: '#9c27b0' }} />
                <Box>
                  <Typography variant="h4" component="div">
                    {analyticsData?.dropoutRisk?.data?.length > 0 
                      ? analyticsData.dropoutRisk.data[analyticsData.dropoutRisk.data.length - 1]?.riskLevel || '0'
                      : '0'
                    }%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Dropout Risk
                  </Typography>
                </Box>
              </FlexBox>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Analytics Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="analytics tabs">
          <Tab 
            icon={<Star />} 
            label="Satisfaction Ratings" 
            iconPosition="start"
          />
          <Tab 
            icon={<People />} 
            label="Dropout Risk" 
            iconPosition="start"
          />
          <Tab 
            icon={<Assessment />} 
            label="Event Success" 
            iconPosition="start"
          />
          <Tab 
            icon={<Timeline />} 
            label="Trends" 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        <Typography variant="h5" gutterBottom>
          Satisfaction Ratings from QR Evaluations
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Real-time satisfaction analytics based on volunteer and beneficiary evaluations submitted through QR codes.
        </Typography>
        
        <FlexBox 
          gap={3} 
          flexWrap="wrap" 
          justifyContent="center"
          sx={{
            '@media (max-width: 1200px)': {
              flexDirection: 'column',
              alignItems: 'center'
            }
          }}
        >
          <PredictiveSatisfactionRatings />
        </FlexBox>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Typography variant="h5" gutterBottom>
          Volunteer Dropout Risk Assessment
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Analysis of volunteer engagement patterns and identification of at-risk volunteers.
        </Typography>
        
        <FlexBox 
          gap={3} 
          flexWrap="wrap" 
          justifyContent="center"
          sx={{
            '@media (max-width: 1200px)': {
              flexDirection: 'column',
              alignItems: 'center'
            }
          }}
        >
          <DropoutRiskAssessment />
        </FlexBox>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Typography variant="h5" gutterBottom>
          Event Success Analytics
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Overview of event completion rates and success metrics.
        </Typography>
        
        <FlexBox 
          gap={3} 
          flexWrap="wrap" 
          justifyContent="center"
          sx={{
            '@media (max-width: 1200px)': {
              flexDirection: 'column',
              alignItems: 'center'
            }
          }}
        >
          <EventSuccessRates />
          <VolunteerDropoutRisk />
        </FlexBox>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Typography variant="h5" gutterBottom>
          Trends & Insights
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Predictive insights and recommendations based on historical data.
        </Typography>
        
        {analyticsData?.insights?.data && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <Insights sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Key Insights
                  </Typography>
                  {analyticsData.insights.data.insights?.length > 0 ? (
                    <Box component="ul" sx={{ pl: 2, m: 0 }}>
                      {analyticsData.insights.data.insights.map((insight: string, index: number) => (
                        <li key={index}>
                          <Typography variant="body2">{insight}</Typography>
                        </li>
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No insights available
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Recommendations
                  </Typography>
                  {analyticsData.insights.data.recommendations?.length > 0 ? (
                    <Box component="ul" sx={{ pl: 2, m: 0 }}>
                      {analyticsData.insights.data.recommendations.map((recommendation: string, index: number) => (
                        <li key={index}>
                          <Typography variant="body2">{recommendation}</Typography>
                        </li>
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No recommendations available
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>
    </PageLayout>
  );
};

export default AnalyticsPage;



































































