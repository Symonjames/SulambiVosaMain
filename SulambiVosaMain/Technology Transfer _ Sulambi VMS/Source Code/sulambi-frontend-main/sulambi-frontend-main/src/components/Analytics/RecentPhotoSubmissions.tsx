import React from 'react';
import FlexBox from '../FlexBox';
import { Typography, Box } from '@mui/material';
import SelectionCard from '../Cards/SelectionCard';
import { InternalReportType, ExternalReportType } from '../../interface/types';

interface RecentPhotoSubmissionsProps {
  reports: (InternalReportType | ExternalReportType)[];
  maxPhotos?: number;
}

const RecentPhotoSubmissions: React.FC<RecentPhotoSubmissionsProps> = ({ 
  reports, 
  maxPhotos = 6 
}) => {
  // Debug logging
  console.log('🔍 RecentPhotoSubmissions - Received reports:', reports);
  console.log('🔍 RecentPhotoSubmissions - Reports count:', reports?.length || 0);
  
  // Filter reports that have photos
  const reportsWithPhotos = reports.filter(report => 
    report.photos && report.photos.length > 0
  ).slice(0, maxPhotos);

  console.log('🔍 RecentPhotoSubmissions - Reports with photos:', reportsWithPhotos);
  console.log('🔍 RecentPhotoSubmissions - Reports with photos count:', reportsWithPhotos.length);

  const hasPhotos = reportsWithPhotos.length > 0;
  
  return (
    <FlexBox
      flexDirection="column"
      borderRadius="10px"
      padding="16px"
      boxShadow="0 0 10px 1px gray"
      minHeight="240px"
      flex="1"
      sx={{
        minWidth: '220px',
        maxWidth: '260px',
        '@media (max-width: 768px)': {
          minWidth: '100%',
          maxWidth: '100%',
        }
      }}
    >
      <Typography textAlign="center" fontWeight="bold" gutterBottom>
        Recent Photo Submissions
      </Typography>
      {hasPhotos ? (
        <Box
          width="100%"
          height="300px"
          sx={{
            overflowY: "auto",
            overflowX: "clip",
            padding: "8px",
          }}
        >
          {reportsWithPhotos.map((report, index) => (
            <SelectionCard
              key={report.id || index}
              enableMarginTop={index > 0}
              hideActions
              textAlign="center"
              header={report.eventId?.title || 'Event'}
              onClickable={() => {
                // Optional: Add click handler for photo viewing
                console.log('View photos for report:', report.id);
              }}
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
            No Photos Available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Photos will appear here once submitted
          </Typography>
        </FlexBox>
      )}
    </FlexBox>
  );
};

export default RecentPhotoSubmissions;
