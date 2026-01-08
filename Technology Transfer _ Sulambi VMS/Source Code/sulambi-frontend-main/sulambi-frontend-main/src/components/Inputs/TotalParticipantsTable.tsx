import React, { useEffect, useMemo } from 'react';
import { Box, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import FlexBox from '../FlexBox';
import { FormDataContext } from '../../contexts/FormDataProvider';
import { useContext } from 'react';

interface TotalParticipantsTableProps {
  required?: boolean;
  error?: boolean;
  disabled?: boolean;
}

const TotalParticipantsTable: React.FC<TotalParticipantsTableProps> = ({
  required = false,
  error = false,
  disabled = false,
}) => {
  const { formData, immutableSetFormData } = useContext(FormDataContext);
  const printBorder = '0.5px solid black';
  const screenBorder = error ? '1px solid red' : '1px solid black';
  const screenCellBorder = '1px solid black';

  const maleTotal = formData.maleTotal || '';
  const femaleTotal = formData.femaleTotal || '';
  
  // Calculate total
  const calculatedTotal = useMemo(() => {
    const male = parseFloat(maleTotal.toString()) || 0;
    const female = parseFloat(femaleTotal.toString()) || 0;
    return male + female;
  }, [maleTotal, femaleTotal]);

  // Update total when male or female changes
  useEffect(() => {
    immutableSetFormData({
      totalParticipants: calculatedTotal > 0 ? calculatedTotal.toString() : '',
    });
  }, [maleTotal, femaleTotal, calculatedTotal, immutableSetFormData]);

  const handleMaleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Enforce max 2 digits (0-99) and digits only
    const raw = String(event.target.value ?? "");
    const digitsOnly = raw.replace(/\D+/g, "").slice(0, 2);
    immutableSetFormData({ maleTotal: digitsOnly });
  };

  const handleFemaleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Enforce max 2 digits (0-99) and digits only
    const raw = String(event.target.value ?? "");
    const digitsOnly = raw.replace(/\D+/g, "").slice(0, 2);
    immutableSetFormData({ femaleTotal: digitsOnly });
  };

  return (
    <FlexBox width="100%" flexDirection="column">
      <Typography color={error ? "red" : "var(--text-landing)"} marginBottom="10px">
        Total Participants
        {required && <b style={{ color: "red" }}>*</b>}
      </Typography>
      <Box
        sx={{
          border: screenBorder,
          borderCollapse: 'collapse',
          overflow: 'hidden',
          width: '100%',
          maxWidth: '400px',
          margin: '10px 0',
          marginLeft: '0.5in',
          backgroundColor: 'white',
          '@media print': {
            margin: '15px 0',
            marginLeft: '0.5in',
            maxWidth: '100%',
            border: error ? '1px solid red' : printBorder,
          },
        }}
      >
        <Table 
          sx={{ 
            width: '100%',
            borderCollapse: 'collapse',
            '& .MuiTableCell-root': {
              border: screenCellBorder,
              borderCollapse: 'collapse',
              '@media print': {
                border: printBorder,
              },
            },
          }}
        >
          <TableHead>
            <TableRow>
              <TableCell
                sx={{
                  backgroundColor: 'white',
                  fontWeight: 'bold',
                  border: screenCellBorder,
                  padding: '5px 8px',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", Times, serif',
                  textAlign: 'left',
                  '@media print': { border: printBorder },
                }}
              >
                Gender
              </TableCell>
              <TableCell
                sx={{
                  backgroundColor: 'white',
                  fontWeight: 'bold',
                  border: screenCellBorder,
                  padding: '5px 8px',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", Times, serif',
                  textAlign: 'center',
                  '@media print': { border: printBorder },
                }}
              >
                Total
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell
                sx={{
                  border: screenCellBorder,
                  padding: '5px 8px',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", Times, serif',
                  textAlign: 'left',
                  backgroundColor: 'white',
                  '@media print': { border: printBorder },
                }}
              >
                Male
              </TableCell>
              <TableCell
                sx={{
                  border: screenCellBorder,
                  padding: '5px 8px',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", Times, serif',
                  textAlign: 'center',
                  backgroundColor: 'white',
                  '@media print': { border: printBorder },
                }}
              >
                <TextField
                  type="text"
                  value={maleTotal}
                  onChange={handleMaleChange}
                  disabled={disabled}
                  error={error}
                  size="small"
                  fullWidth
                  inputProps={{
                    inputMode: "numeric",
                    pattern: "[0-9]*",
                    style: {
                      fontSize: '10pt',
                      fontFamily: '"Times New Roman", Times, serif',
                      textAlign: 'center',
                    },
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontSize: '10pt',
                      fontFamily: '"Times New Roman", Times, serif',
                      backgroundColor: 'white',
                      '& fieldset': {
                        border: 'none',
                      },
                    },
                  }}
                />
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell
                sx={{
                  border: screenCellBorder,
                  padding: '5px 8px',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", Times, serif',
                  textAlign: 'left',
                  backgroundColor: 'white',
                  '@media print': { border: printBorder },
                }}
              >
                Female
              </TableCell>
              <TableCell
                sx={{
                  border: screenCellBorder,
                  padding: '5px 8px',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", Times, serif',
                  textAlign: 'center',
                  backgroundColor: 'white',
                  '@media print': { border: printBorder },
                }}
              >
                <TextField
                  type="text"
                  value={femaleTotal}
                  onChange={handleFemaleChange}
                  disabled={disabled}
                  error={error}
                  size="small"
                  fullWidth
                  inputProps={{
                    inputMode: "numeric",
                    pattern: "[0-9]*",
                    style: {
                      fontSize: '10pt',
                      fontFamily: '"Times New Roman", Times, serif',
                      textAlign: 'center',
                    },
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontSize: '10pt',
                      fontFamily: '"Times New Roman", Times, serif',
                      backgroundColor: 'white',
                      '& fieldset': {
                        border: 'none',
                      },
                    },
                  }}
                />
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell
                sx={{
                  border: screenCellBorder,
                  padding: '5px 8px',
                  fontWeight: 'bold',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", Times, serif',
                  textAlign: 'left',
                  backgroundColor: 'white',
                  '@media print': { border: printBorder },
                }}
              >
                Total
              </TableCell>
              <TableCell
                sx={{
                  border: screenCellBorder,
                  padding: '5px 8px',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", Times, serif',
                  textAlign: 'center',
                  backgroundColor: 'white',
                  '@media print': { border: printBorder },
                }}
              >
                <TextField
                  type="number"
                  value={calculatedTotal || ''}
                  disabled={true}
                  error={error}
                  size="small"
                  fullWidth
                  inputProps={{
                    min: 0,
                    readOnly: true,
                    style: {
                      fontSize: '10pt',
                      fontFamily: '"Times New Roman", Times, serif',
                      textAlign: 'center',
                      fontWeight: 'bold',
                    },
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontSize: '10pt',
                      fontFamily: '"Times New Roman", Times, serif',
                      backgroundColor: 'white',
                      '& fieldset': {
                        border: 'none',
                      },
                    },
                  }}
                />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </Box>
    </FlexBox>
  );
};

export default TotalParticipantsTable;

