import React, { useState, useEffect } from 'react';
import { Typography, CircularProgress, Alert } from '@mui/material';
import { BarChart } from '@mui/x-charts';
import FlexBox from '../FlexBox';
import { getEventSuccessAnalytics } from '../../api/analytics';

const EventSuccessRates: React.FC = () => {
  const [chartData, setChartData] = useState<any[]>([]);
  const [hasData, setHasData] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadEventSuccessData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await getEventSuccessAnalytics();
        
        if (response.success) {
          const data = response.data;
          const successData = [
            { id: 'completed', value: data.completed || 0, label: 'Completed', color: '#4caf50' },
            { id: 'cancelled', value: data.cancelled || 0, label: 'Cancelled', color: '#f44336' },
            { id: 'inProgress', value: data.inProgress || 0, label: 'In Progress', color: '#ff9800' }
          ];
          
          setChartData(successData);
          setHasData(true);
        } else {
          setError('Failed to load event success data');
        }
      } catch (err) {
        console.error('Error loading event success data:', err);
        setError('Error loading event success data');
      } finally {
        setLoading(false);
      }
    };

    loadEventSuccessData();
  }, []);

  // Compute predictive message
  let message: { text: string; good: boolean } | null = null;
  if (hasData && chartData.length > 0) {
    const completed = chartData.find(d => d.id === 'completed')?.value || 0;
    const cancelled = chartData.find(d => d.id === 'cancelled')?.value || 0;
    const inProgress = chartData.find(d => d.id === 'inProgress')?.value || 0;
    const total = completed + cancelled + inProgress || 1;
    const completionRate = completed / total;
    message = completionRate >= 0.5
      ? { text: '✅ Great job! Most events are being completed successfully.', good: true }
      : { text: '⚠️ Attention: Event completion rates are dropping. Action may be needed.', good: false };
  }

  if (loading) {
    return (
      <FlexBox
        flexDirection="column"
        borderRadius="10px"
        padding="16px"
        boxShadow="0 0 10px 1px gray"
        minHeight="360px"
        flex="1"
        alignItems="center"
        justifyContent="center"
        sx={{
          minWidth: '300px',
          maxWidth: '340px',
          '@media (max-width: 768px)': {
            minWidth: '100%',
            maxWidth: '100%',
          }
        }}
      >
        <CircularProgress size={40} />
        <Typography variant="body2" color="text.secondary" mt={2}>
          Loading event success data...
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
        minHeight="360px"
        flex="1"
        sx={{
          minWidth: '300px',
          maxWidth: '340px',
          '@media (max-width: 768px)': {
            minWidth: '100%',
            maxWidth: '100%',
          }
        }}
      >
        <Typography textAlign="center" fontWeight="bold" gutterBottom>
          Event Success Rates
        </Typography>
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      </FlexBox>
    );
  }

  return (
    <FlexBox
      flexDirection="column"
      borderRadius="10px"
      padding="16px"
      boxShadow="0 0 10px 1px gray"
      minHeight="360px"
      flex="1"
      sx={{
        minWidth: '300px',
        maxWidth: '340px',
        '@media (max-width: 768px)': {
          minWidth: '100%',
          maxWidth: '100%',
        }
      }}
    >
      <Typography textAlign="center" fontWeight="bold" gutterBottom>
        Event Success Rates
      </Typography>
      {hasData ? (
        <FlexBox alignItems="center" justifyContent="center" height="100%" sx={{ minHeight: '300px' }}>
          <BarChart
            height={300}
            width={320}
            xAxis={[{ scaleType: 'band', data: chartData.map(d => d.label) }]}
            series={[{ data: chartData.map(d => d.value), color: '#c07e00' }]}
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
            Analytics will appear here once events are created
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

export default EventSuccessRates;