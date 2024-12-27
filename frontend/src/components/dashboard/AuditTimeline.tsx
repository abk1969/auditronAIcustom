import React from 'react';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import { Typography, Box } from '@mui/material';
import { SecurityOutlined, BugReport, CheckCircle } from '@mui/icons-material';

const mockAudits = [
  {
    id: 1,
    date: '2024-04-15',
    type: 'scan',
    description: 'Scan de sécurité complet',
    status: 'completed',
  },
  {
    id: 2,
    date: '2024-04-14',
    type: 'issue',
    description: 'Vulnérabilité SQL détectée',
    status: 'warning',
  },
  {
    id: 3,
    date: '2024-04-13',
    type: 'resolution',
    description: 'Correction des failles XSS',
    status: 'success',
  },
];

const getTimelineDot = (type: string) => {
  switch (type) {
    case 'scan':
      return (
        <TimelineDot sx={{ bgcolor: 'primary.main' }}>
          <SecurityOutlined />
        </TimelineDot>
      );
    case 'issue':
      return (
        <TimelineDot sx={{ bgcolor: 'warning.main' }}>
          <BugReport />
        </TimelineDot>
      );
    case 'resolution':
      return (
        <TimelineDot sx={{ bgcolor: 'success.main' }}>
          <CheckCircle />
        </TimelineDot>
      );
    default:
      return <TimelineDot />;
  }
};

export const AuditTimeline: React.FC = () => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Chronologie des Audits
      </Typography>
      <Timeline>
        {mockAudits.map((audit, index) => (
          <TimelineItem key={audit.id}>
            <TimelineSeparator>
              {getTimelineDot(audit.type)}
              {index < mockAudits.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" component="span">
                {audit.date}
              </Typography>
              <Typography>{audit.description}</Typography>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Box>
  );
}; 