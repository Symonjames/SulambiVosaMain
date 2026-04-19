import React from 'react';
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Container,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Groups, TrendingUp, DesignServices } from '@mui/icons-material';

/** Fictitious values for layout and stakeholder review only. */
const DESIGN_VOLUNTEER_COUNT = 35;
const DESIGN_VOLUNTEER_SCORE = 4.3;
const DESIGN_BENEFICIARY_COUNT = 12;
const DESIGN_BENEFICIARY_SCORE = 4.1;
const DESIGN_OVERALL = 4.25;
const DESIGN_YEAR_LABEL = '2026';

const semesterRows = [
  { semester: '2026-1', events: 'Outreach — Batangas, Skills workshop, Community pantry', extra: 2 },
  { semester: '2026-2', events: 'Youth camp, Health screening day', extra: 0 },
];

/**
 * Static design preview: predictive satisfaction panel when ~35 volunteer evaluations exist.
 * Open at `/design/predictive-satisfaction` — not wired to the API.
 */
const PredictiveSatisfactionRatingsDesignPage: React.FC = () => {
  const volunteerPct = (DESIGN_VOLUNTEER_SCORE / 5) * 100;
  const beneficiaryPct = (DESIGN_BENEFICIARY_SCORE / 5) * 100;
  const overallPct = (DESIGN_OVERALL / 5) * 100;

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.100', py: 3, px: 2 }}>
      <Container maxWidth="md">
        <Alert severity="warning" icon={<DesignServices />} sx={{ mb: 2 }}>
          <Typography variant="subtitle2" fontWeight="bold">
            Design preview only
          </Typography>
          <Typography variant="body2">
            All figures—including {DESIGN_VOLUNTEER_COUNT} volunteer evaluations—are fictitious. This page does not
            read from your database or analytics API.
          </Typography>
        </Alert>

        <Card
          elevation={2}
          sx={{
            borderRadius: 2,
            overflow: 'hidden',
            border: (theme) => `1px solid ${alpha(theme.palette.primary.main, 0.12)}`,
          }}
        >
          <Box
            sx={{
              px: 2,
              py: 1.5,
              background: (theme) =>
                `linear-gradient(110deg, ${alpha(theme.palette.primary.main, 0.08)} 0%, ${alpha(theme.palette.secondary.main, 0.06)} 100%)`,
              borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
            }}
          >
            <Stack direction="row" alignItems="center" justifyContent="space-between" flexWrap="wrap" gap={1}>
              <Stack direction="row" alignItems="center" gap={1}>
                <Groups color="primary" />
                <Typography fontWeight="bold">Predictive satisfaction ratings</Typography>
                <Chip label="Layout mock" size="small" color="default" variant="outlined" />
              </Stack>
              <Chip label={DESIGN_YEAR_LABEL} size="small" color="primary" variant="outlined" />
            </Stack>
          </Box>

          <CardContent sx={{ p: 2.5 }}>
            {/* Volunteer cohort — visual emphasis for “35 volunteers” */}
            <PaperSection title="Volunteer evaluations" subtitle="Cohort at a glance (design)">
              <Stack direction="row" alignItems="flex-start" justifyContent="space-between" gap={2} flexWrap="wrap">
                <Box sx={{ flex: '1 1 200px' }}>
                  <Typography variant="h3" component="p" fontWeight="800" color="primary.dark" lineHeight={1.1}>
                    {DESIGN_VOLUNTEER_SCORE.toFixed(1)}
                    <Typography component="span" variant="h5" color="text.secondary" fontWeight={600}>
                      /5
                    </Typography>
                  </Typography>
                  <Stack direction="row" alignItems="center" gap={0.75} mt={0.5}>
                    <Chip
                      icon={<Groups sx={{ fontSize: 18 }} />}
                      label={`${DESIGN_VOLUNTEER_COUNT} volunteers`}
                      color="primary"
                      size="small"
                      sx={{ fontWeight: 600 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      Average from volunteer forms
                    </Typography>
                  </Stack>
                </Box>
                <Box
                  sx={{
                    flex: '1 1 220px',
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 0.5,
                    justifyContent: 'flex-end',
                    alignContent: 'flex-start',
                    maxWidth: 280,
                  }}
                  aria-hidden
                >
                  {Array.from({ length: DESIGN_VOLUNTEER_COUNT }).map((_, i) => (
                    <Box
                      key={i}
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: (theme) =>
                          i % 5 === 0
                            ? theme.palette.primary.main
                            : alpha(theme.palette.primary.main, 0.35 + (i % 4) * 0.08),
                      }}
                    />
                  ))}
                </Box>
              </Stack>
              <LinearProgress
                variant="determinate"
                value={volunteerPct}
                sx={{
                  mt: 2,
                  height: 10,
                  borderRadius: 5,
                  bgcolor: (theme) => alpha(theme.palette.primary.main, 0.12),
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 5,
                    background: (theme) =>
                      `linear-gradient(90deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.light} 100%)`,
                  },
                }}
              />
            </PaperSection>

            <Stack spacing={2.5} sx={{ mt: 2 }}>
              <MetricRow
                label="Overall satisfaction"
                score={DESIGN_OVERALL}
                countLabel={`${DESIGN_VOLUNTEER_COUNT + DESIGN_BENEFICIARY_COUNT} responses (mock)`}
                barHeight={8}
                pct={overallPct}
                barSx={{
                  bgcolor: (theme) => alpha(theme.palette.success.main, 0.15),
                  '& .MuiLinearProgress-bar': {
                    bgcolor: 'success.main',
                  },
                }}
              />
              <MetricRow
                label="Beneficiaries"
                score={DESIGN_BENEFICIARY_SCORE}
                countLabel={`${DESIGN_BENEFICIARY_COUNT} ratings (mock)`}
                barHeight={6}
                pct={beneficiaryPct}
                barSx={{
                  bgcolor: (theme) => alpha(theme.palette.secondary.main, 0.12),
                  '& .MuiLinearProgress-bar': {
                    background: (theme) =>
                      `linear-gradient(90deg, ${theme.palette.secondary.dark} 0%, ${theme.palette.secondary.light} 100%)`,
                  },
                }}
              />
            </Stack>

            <Stack direction="row" alignItems="center" gap={1} sx={{ mt: 3, mb: 1 }}>
              <TrendingUp color="success" fontSize="small" />
              <Typography variant="subtitle2" fontWeight="bold">
                Trend (sample)
              </Typography>
              <Chip label="Stable" size="small" sx={{ bgcolor: 'success.main', color: 'common.white' }} />
            </Stack>

            <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
              Semesters (mock labels)
            </Typography>
            <Stack spacing={1.25}>
              {semesterRows.map((row) => (
                <Box
                  key={row.semester}
                  sx={{
                    p: 1.5,
                    borderRadius: 1,
                    border: (theme) => `1px solid ${theme.palette.divider}`,
                    bgcolor: 'background.paper',
                  }}
                >
                  <Typography variant="body2" fontWeight="bold" gutterBottom>
                    {row.semester}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" fontSize="0.875rem">
                    {row.events}
                    {row.extra > 0 ? (
                      <Chip label={`+${row.extra} more`} size="small" sx={{ ml: 1, height: 20, fontSize: '0.65rem' }} />
                    ) : null}
                  </Typography>
                </Box>
              ))}
            </Stack>

            <Typography variant="subtitle2" fontWeight="bold" sx={{ mt: 2 }} gutterBottom>
              Top issues (placeholder copy)
            </Typography>
            <Stack spacing={0.75}>
              {['Scheduling & reminders', 'Venue directions', 'Materials handout'].map((issue, i) => (
                <Stack key={issue} direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" fontSize="0.875rem">
                    {issue}
                  </Typography>
                  <Chip label={String(4 - i)} size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                </Stack>
              ))}
            </Stack>
          </CardContent>
        </Card>

        <Typography variant="caption" color="text.secondary" display="block" textAlign="center" sx={{ mt: 2 }}>
          Production UI: Admin → Analytics, or dashboard widget. This route is for design review only.
        </Typography>
      </Container>
    </Box>
  );
};

function PaperSection({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <Box
      sx={{
        p: 2,
        borderRadius: 2,
        bgcolor: (theme) => alpha(theme.palette.primary.main, 0.04),
        border: (theme) => `1px solid ${alpha(theme.palette.primary.main, 0.14)}`,
      }}
    >
      <Typography variant="subtitle2" fontWeight="bold" color="primary.dark">
        {title}
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1.5 }}>
        {subtitle}
      </Typography>
      {children}
    </Box>
  );
}

function MetricRow({
  label,
  score,
  countLabel,
  pct,
  barHeight,
  barSx,
}: {
  label: string;
  score: number;
  countLabel: string;
  pct: number;
  barHeight: number;
  barSx: object;
}) {
  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="baseline" mb={0.5}>
        <Typography variant="body2" fontWeight={600}>
          {label}: {score.toFixed(1)}/5.0
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {countLabel}
        </Typography>
      </Stack>
      <LinearProgress variant="determinate" value={pct} sx={{ height: barHeight, borderRadius: barHeight / 2, ...barSx }} />
    </Box>
  );
}

export default PredictiveSatisfactionRatingsDesignPage;
