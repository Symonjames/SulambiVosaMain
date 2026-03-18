import React, { useState, useEffect } from 'react';
import { Typography } from '@mui/material';
import { LineChart } from '@mui/x-charts/LineChart';
import FlexBox from '../FlexBox';

const VolunteerDropoutRisk: React.FC = () => {
  const [chartData, setChartData] = useState<any>(null);
  const [hasData, setHasData] = useState(false);

  useEffect(() => {
    // Mock data for demonstration
    const mockData = {
      months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      riskLevels: [15, 18, 22, 19, 25, 28],
      activeVolunteers: [120, 135, 145, 158, 165, 170]
    };
    
    setChartData(mockData);
    setHasData(true);
  }, []);

  // Predictive message based on trend
  let message: { text: string; good: boolean } | null = null;
  if (hasData && chartData?.riskLevels?.length) {
    const arr = chartData.riskLevels as number[];
    const last = arr[arr.length - 1];
    const first = arr[0];
    const avg = arr.reduce((a, b) => a + b, 0) / arr.length;
    const rising = last > first && last - first >= 3; // simple slope check
    const high = last >= 22 || avg >= 20; // threshold heuristic
    if (!rising && !high) {
      message = { text: '✅ Volunteer retention is stable. Keep up the good work.', good: true };
    } else {
      message = { text: '⚠️ Volunteer dropout risk is elevated or rising. Consider engagement measures.', good: false };
    }
  }

  return (
    <FlexBox
      flexDirection="column"
      borderRadius="10px"
      padding="16px"
      boxShadow="0 0 10px 1px gray"
      minHeight="300px"
      flex="1"
      sx={{
        minWidth: '260px',
        maxWidth: '300px',
        '@media (max-width: 768px)': {
          minWidth: '100%',
          maxWidth: '100%',
        }
      }}
    >
      <Typography textAlign="center" fontWeight="bold" gutterBottom>
        Volunteer Dropout Risk
      </Typography>
      {hasData ? (
        <FlexBox alignItems="center" justifyContent="center" height="100%" sx={{ minHeight: '240px' }}>
          <LineChart
            height={240}
            width={260}
            series={[
              {
                data: chartData.riskLevels,
                label: 'Risk %',
                color: '#C07F00',
                curve: 'monotone',
              }
            ]}
            xAxis={[
              {
                scaleType: 'point',
                data: chartData.months,
              }
            ]}
            yAxis={[
              {
                label: 'Risk %',
                min: 0,
                max: 30,
              }
            ]}
            grid={{ vertical: true, horizontal: true }}
          />
        </FlexBox>
      ) : (
        <FlexBox
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          height="260px"
          sx={{ color: 'text.secondary' }}
        >
          <Typography variant="h6" color="text.secondary">
            No Data Available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Analytics will appear here once volunteers register
          </Typography>
        </FlexBox>
      )}
      {message && (
        <Typography mt={1} variant="body2" color={message.good ? 'success.main' : 'warning.main'}>
          {message.text}
        </Typography>
      )}
    </FlexBox>
  );
};

export default VolunteerDropoutRisk;