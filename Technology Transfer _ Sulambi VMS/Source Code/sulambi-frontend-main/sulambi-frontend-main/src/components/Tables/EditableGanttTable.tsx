import React, { useState, useEffect, useContext, useCallback, useRef } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField,
  Box,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import FlexBox from '../FlexBox';
import { FormDataContext } from '../../contexts/FormDataProvider';

interface EditableGanttTableProps {
  fieldKey: string;
  initialData?: { [rowIndex: string]: { [colKey: string]: string } };
  initialColumns?: string[];
  viewOnly?: boolean;
}

const EditableGanttTable: React.FC<EditableGanttTableProps> = ({
  fieldKey,
  initialData = {},
  initialColumns = ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'],
  viewOnly = false,
}) => {
  const { immutableSetFormData } = useContext(FormDataContext);
  const isInitialized = useRef(false);
  const updateTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  
  // Initialize columns - extract from initialData if available, otherwise use initialColumns
  const [columns, setColumns] = useState<string[]>(() => {
    // If we have initialData, extract column names from the row keys
    if (Object.keys(initialData).length > 0) {
      const extractedColumns: string[] = [];
      const columnSet = new Set<string>();
      
      // Get all unique column keys from all rows
      Object.keys(initialData).forEach((rowIndex) => {
        const row = initialData[rowIndex];
        if (row) {
          Object.keys(row).forEach((colKey) => {
            if (!columnSet.has(colKey)) {
              columnSet.add(colKey);
              extractedColumns.push(colKey);
            }
          });
        }
      });
      
      // Preserve column order from data - don't sort if there are custom names
      // Only sort if ALL columns are default format (Month X or act_X)
      const allAreDefaultFormat = extractedColumns.every(col => 
        col === 'Activities' || col === 'activities' || /^Month \d+$/.test(col) || /^act_\d+$/.test(col)
      );
      
      if (allAreDefaultFormat) {
        // Only sort if all are default format
        extractedColumns.sort((a, b) => {
          if (a === 'Activities' || a === 'activities') return -1;
          if (b === 'Activities' || b === 'activities') return 1;
          
          const numA = parseInt(a.replace(/Month |act_/g, '')) || 0;
          const numB = parseInt(b.replace(/Month |act_/g, '')) || 0;
          
          if (numA > 0 && numB > 0) {
            return numA - numB;
          }
          return 0;
        });
      }
      // Otherwise preserve the order as it appears in the data
      
      if (extractedColumns.length > 0) {
        return extractedColumns;
      }
    }
    
    // Fallback to initialColumns or default
    if (initialColumns.length > 0) {
      return initialColumns;
    }
    return ['Activities', 'Month 1', 'Month 2', 'Month 3'];
  });
  
  // Track column name changes for controlled inputs - use columns directly as initial state
  const [columnNames, setColumnNames] = useState<{ [key: string]: string }>(() => {
    const names: { [key: string]: string } = {};
    columns.forEach((col, idx) => {
      names[`col-${idx}`] = col;
    });
    return names;
  });
  
  // Sync columnNames when columns array length changes (e.g., when columns are added/deleted)
  // This effect only runs when columns are added/deleted, not when column names change
  useEffect(() => {
    const newNames: { [key: string]: string } = {};
    columns.forEach((col, idx) => {
      const key = `col-${idx}`;
      // Always preserve existing name if it exists (user edits), otherwise use column name
      if (columnNames[key]) {
        newNames[key] = columnNames[key];
      } else {
        newNames[key] = col;
      }
    });
    // Only update if the structure changed (column count changed)
    const currentKeys = Object.keys(columnNames).sort();
    const newKeys = Object.keys(newNames).sort();
    if (currentKeys.length !== newKeys.length || currentKeys.join(',') !== newKeys.join(',')) {
      setColumnNames(newNames);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [columns.length]); // Only update when column count changes - intentionally not including columnNames

  const [rows, setRows] = useState<{ [rowIndex: string]: { [colKey: string]: string } }>(() => {
    if (Object.keys(initialData).length > 0) {
      isInitialized.current = true;
      return initialData;
    }
    return {};
  });

  const [rowCount, setRowCount] = useState(() => {
    const existingRows = Object.keys(initialData);
    return existingRows.length > 0 ? Math.max(...existingRows.map(r => parseInt(r) || 0)) + 1 : 0;
  });

  // Only initialize from props once, don't reset on prop changes
  useEffect(() => {
    if (!isInitialized.current && Object.keys(initialData).length > 0) {
      setRows(initialData);
      isInitialized.current = true;
    }
  }, []); // Empty dependency array - only run on mount
  
  // Mark as initialized after first render to prevent resets
  useEffect(() => {
    isInitialized.current = true;
  }, []);

  // Update form data whenever rows or columns change (debounced to prevent focus loss)
  useEffect(() => {
    // Clear any pending updates
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }
    
    // Only update if component is initialized (to avoid updating during initial mount)
    if (isInitialized.current) {
      updateTimeoutRef.current = setTimeout(() => {
        // Save rows data - column names are already in the row keys when renamed
        // When columns are renamed, the row keys are updated, so column names persist in the data
        immutableSetFormData({ 
          [fieldKey]: rows
        });
      }, 300);
    }
    
    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, [rows, columns, fieldKey, immutableSetFormData]);

  const handleCellChange = useCallback((rowIndex: string, colKey: string, value: string) => {
    setRows((prev) => {
      const newRows = { ...prev };
      if (!newRows[rowIndex]) {
        newRows[rowIndex] = {};
      }
      newRows[rowIndex] = {
        ...newRows[rowIndex],
        [colKey]: value,
      };
      return newRows;
    });
  }, []);

  const handleAddRow = () => {
    const newRowIndex = rowCount.toString();
    const newRow: { [colKey: string]: string } = {};
    columns.forEach((col) => {
      newRow[col] = '';
    });
    setRows((prev) => ({
      ...prev,
      [newRowIndex]: newRow,
    }));
    setRowCount((prev) => prev + 1);
  };

  const handleDeleteRow = (rowIndex: string) => {
    setRows((prev) => {
      const newRows = { ...prev };
      delete newRows[rowIndex];
      return newRows;
    });
  };

  const handleAddColumn = () => {
    const newColumnName = `Month ${columns.length}`;
    setColumns((prev) => [...prev, newColumnName]);
    
    // Initialize new column for all existing rows
    setRows((prev) => {
      const newRows = { ...prev };
      Object.keys(newRows).forEach((rowIndex) => {
        newRows[rowIndex] = {
          ...newRows[rowIndex],
          [newColumnName]: '',
        };
      });
      return newRows;
    });
  };

  const handleDeleteColumn = useCallback((colKey: string) => {
    // Don't allow deleting the first column (Activities)
    setColumns((prev) => {
      const index = prev.indexOf(colKey);
      if (index === 0 || index === -1) return prev; // Don't delete first column or if not found
      return prev.filter((col) => col !== colKey);
    });
    
    // Remove column from all rows using functional update
    setRows((prev) => {
      const newRows: { [rowIndex: string]: { [colKey: string]: string } } = {};
      Object.keys(prev).forEach((rowIndex) => {
        const rowData = { ...prev[rowIndex] };
        if (colKey in rowData) {
          const { [colKey]: removed, ...rest } = rowData;
          newRows[rowIndex] = rest;
        } else {
          newRows[rowIndex] = rowData;
        }
      });
      return newRows;
    });
  }, []);

  const handleColumnRename = useCallback((colIndex: number, oldName: string, newName: string, updateRows: boolean = true) => {
    // Update the column name immediately in columnNames state for instant UI feedback
    const key = `col-${colIndex}`;
    setColumnNames((prev) => {
      // Only update if value actually changed
      if (prev[key] === newName) return prev;
      return {
        ...prev,
        [key]: newName
      };
    });
    
    // Only update columns and rows if explicitly requested (e.g., on blur)
    // This prevents focus loss during typing
    if (updateRows) {
      // Update columns state
      setColumns((prev) => {
        // Only update if value actually changed
        if (prev[colIndex] === newName) return prev;
        const newColumns = [...prev];
        newColumns[colIndex] = newName;
        return newColumns;
      });
      
      // Update all rows with new column name
      if (oldName !== newName) {
        setRows((prev) => {
          const newRows: { [rowIndex: string]: { [colKey: string]: string } } = {};
          Object.keys(prev).forEach((rowIndex) => {
            newRows[rowIndex] = { ...prev[rowIndex] };
            if (oldName in newRows[rowIndex]) {
              // Copy value from old key to new key
              newRows[rowIndex][newName] = newRows[rowIndex][oldName];
              // Delete old key
              delete newRows[rowIndex][oldName];
            }
          });
          return newRows;
        });
      }
    }
  }, []);

  const rowIndices = Object.keys(rows).sort((a, b) => parseInt(a) - parseInt(b));

  return (
    <Box sx={{ 
      width: '100%', 
      overflowX: viewOnly ? 'visible' : 'auto',
      '@media print': {
        overflow: 'visible',
        width: '100%',
        maxWidth: '100%',
        margin: 0,
        padding: 0,
      }
    }}>
      <TableContainer 
        component={viewOnly ? 'div' : Paper}
        sx={{ 
          maxHeight: viewOnly ? 'none' : '400px', 
          overflow: viewOnly ? 'visible' : 'auto',
          width: '100%',
          '@media print': {
            overflow: 'visible',
            maxHeight: 'none',
            pageBreakInside: 'avoid',
            boxShadow: 'none',
            width: '100%',
            maxWidth: '100%',
            margin: 0,
            padding: 0,
          }
        }}
      >
        <Table 
          stickyHeader={!viewOnly} 
          className={viewOnly ? 'bsuFormChild' : undefined}
          sx={{ 
            minWidth: viewOnly ? 'auto' : 650,
            width: '100%',
            ...(viewOnly && {
              fontFamily: '"Times New Roman", Times, serif',
              borderCollapse: 'collapse',
              fontSize: '9pt',
              tableLayout: 'fixed',
              border: '1px solid black',
              borderTop: 'none',
              margin: '0 0 10px 0',
            }),
            '@media print': {
              width: '100%',
              maxWidth: '100%',
              tableLayout: viewOnly ? 'fixed' : 'auto',
              fontSize: viewOnly ? '9pt' : '0.6rem',
              fontFamily: viewOnly ? '"Times New Roman", Times, serif' : undefined,
            }
          }} 
          size="small"
        >
          <TableHead>
            <TableRow>
              {columns.map((col, colIndex) => (
                <TableCell
                  key={`header-cell-${colIndex}`}
                  className={viewOnly ? 'fontSet' : undefined}
                  sx={{
                    backgroundColor: viewOnly ? 'transparent' : '#f5f5f5',
                    fontWeight: viewOnly ? '700' : 'bold',
                    minWidth: colIndex === 0 ? '120px' : '80px',
                    maxWidth: colIndex === 0 ? '120px' : '80px',
                    padding: viewOnly ? '6px 8px' : '2px 4px',
                    fontSize: viewOnly ? '9pt' : '0.7rem',
                    position: viewOnly ? 'static' : 'sticky',
                    zIndex: colIndex === 0 && !viewOnly ? 2 : 1,
                    left: colIndex === 0 && !viewOnly ? 0 : 'auto',
                    border: viewOnly ? '1px solid black' : '1px solid #e0e0e0',
                    borderRight: viewOnly ? '1px solid black' : '1px solid #e0e0e0',
                    ...(viewOnly && { borderTop: '1px solid black' }),
                    whiteSpace: 'normal',
                    wordWrap: 'break-word',
                    overflowWrap: 'break-word',
                    ...(viewOnly && { wordBreak: 'break-word' }),
                    ...(viewOnly && { fontFamily: '"Times New Roman", Times, serif' }),
                    ...(viewOnly && { verticalAlign: 'top' }),
                    ...(viewOnly && { lineHeight: '1.4' }),
                    '@media print': {
                      padding: viewOnly ? '6px 8px' : '1px 2px',
                      fontSize: viewOnly ? '9pt' : '0.6rem',
                      position: 'static',
                      border: '1px solid black',
                      borderRight: '1px solid black',
                      ...(viewOnly && { borderTop: '1px solid black' }),
                      minWidth: 'auto',
                      maxWidth: 'auto',
                      width: 'auto',
                      ...(viewOnly && { fontFamily: '"Times New Roman", Times, serif' }),
                    }
                  }}
                >
                  {viewOnly ? (
                    col
                  ) : colIndex === 0 ? (
                    <TextField
                      key={`header-col-${colIndex}`}
                      value={columnNames[`col-${colIndex}`] ?? col}
                      onChange={(e) => {
                        e.stopPropagation();
                        const newValue = e.target.value;
                        const currentName = columnNames[`col-${colIndex}`] ?? col;
                        // Only update columnNames during typing, not columns/rows (prevents focus loss)
                        handleColumnRename(colIndex, currentName, newValue, false);
                      }}
                      onKeyDown={(e) => {
                        e.stopPropagation();
                      }}
                      onKeyUp={(e) => {
                        e.stopPropagation();
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                      }}
                      onFocus={(e) => {
                        e.stopPropagation();
                      }}
                      autoFocus={false}
                      size="small"
                      sx={{
                        '& .MuiInputBase-input': {
                          padding: '2px 4px',
                          fontWeight: 'bold',
                          fontSize: '0.7rem',
                        },
                      }}
                        onBlur={(e) => {
                          const finalValue = e.target.value.trim();
                          // If empty on blur, restore to a default name
                          const finalName = finalValue || (colIndex === 0 ? 'Activities' : `Month ${colIndex}`);
                          // Get the actual current column name from columns array (not columnNames which might be stale)
                          const currentColumnName = columns[colIndex];
                          // Now update columns and rows with the final value
                          handleColumnRename(colIndex, currentColumnName, finalName, true);
                        }}
                    />
                  ) : (
                    <FlexBox alignItems="center" gap={1}>
                      <TextField
                        key={`header-col-${colIndex}`}
                        value={columnNames[`col-${colIndex}`] ?? col}
                        onChange={(e) => {
                          e.stopPropagation();
                          const newValue = e.target.value;
                          const currentName = columnNames[`col-${colIndex}`] ?? col;
                          // Only update columnNames during typing, not columns/rows (prevents focus loss)
                          handleColumnRename(colIndex, currentName, newValue, false);
                        }}
                        onKeyDown={(e) => {
                          e.stopPropagation();
                        }}
                        onKeyUp={(e) => {
                          e.stopPropagation();
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                        }}
                        onFocus={(e) => {
                          e.stopPropagation();
                        }}
                        autoFocus={false}
                        size="small"
                        sx={{
                          flex: 1,
                          '& .MuiInputBase-input': {
                            padding: '2px 4px',
                            fontWeight: 'bold',
                            fontSize: '0.7rem',
                          },
                        }}
                        onBlur={(e) => {
                          const finalValue = e.target.value.trim();
                          // If empty on blur, restore to a default name
                          const finalName = finalValue || (colIndex === 0 ? 'Activities' : `Month ${colIndex}`);
                          // Get the actual current column name from columns array (not columnNames which might be stale)
                          const currentColumnName = columns[colIndex];
                          // Now update columns and rows with the final value
                          handleColumnRename(colIndex, currentColumnName, finalName, true);
                        }}
                      />
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteColumn(col);
                        }}
                        sx={{ padding: '2px' }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </FlexBox>
                  )}
                </TableCell>
              ))}
              {!viewOnly && (
                <TableCell
                    sx={{
                      backgroundColor: '#f5f5f5',
                      fontWeight: 'bold',
                      minWidth: '40px',
                      padding: '4px',
                      position: 'sticky',
                      right: 0,
                      zIndex: 2,
                    }}
                >
                  <IconButton
                    size="small"
                    onClick={handleAddColumn}
                    sx={{ padding: '4px' }}
                    title="Add Column"
                  >
                    <AddIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              )}
            </TableRow>
          </TableHead>
          <TableBody>
            {rowIndices.map((rowIndex) => (
              <TableRow 
                key={rowIndex} 
                hover={!viewOnly}
                sx={{
                  '@media print': {
                    pageBreakInside: 'avoid',
                    breakInside: 'avoid',
                  }
                }}
              >
                {columns.map((col, colIndex) => (
                  <TableCell
                    key={`body-cell-${rowIndex}-${colIndex}`}
                    className={viewOnly ? 'fontSet' : undefined}
                    sx={{
                      border: viewOnly ? '1px solid black' : '1px solid #e0e0e0',
                      borderRight: viewOnly ? '1px solid black' : '1px solid #e0e0e0',
                      ...(viewOnly && { borderTop: 'none' }),
                      padding: viewOnly ? '6px 8px' : '2px 3px',
                      position: colIndex === 0 && !viewOnly ? 'sticky' : 'static',
                      left: colIndex === 0 && !viewOnly ? 0 : 'auto',
                      backgroundColor: viewOnly ? 'transparent' : (colIndex === 0 ? '#fafafa' : 'white'),
                      zIndex: colIndex === 0 && !viewOnly ? 1 : 0,
                      fontSize: viewOnly ? '9pt' : '0.7rem',
                      lineHeight: viewOnly ? '1.4' : '1.3',
                      whiteSpace: 'normal',
                      wordWrap: 'break-word',
                      overflowWrap: 'break-word',
                      ...(viewOnly && { wordBreak: 'break-word' }),
                      minWidth: colIndex === 0 ? '120px' : '80px',
                      maxWidth: colIndex === 0 ? '120px' : '80px',
                      ...(viewOnly && { fontFamily: '"Times New Roman", Times, serif' }),
                      ...(viewOnly && { textAlign: 'center' }),
                      ...(viewOnly && { verticalAlign: 'top' }),
                      '@media print': {
                        padding: viewOnly ? '6px 8px' : '1px 2px',
                        fontSize: viewOnly ? '9pt' : '0.6rem',
                        lineHeight: viewOnly ? '1.4' : '1.1',
                        pageBreakInside: 'avoid',
                        border: '1px solid black',
                        borderRight: '1px solid black',
                        ...(viewOnly && { borderTop: 'none' }),
                        minWidth: 'auto',
                        maxWidth: 'auto',
                        width: 'auto',
                        position: 'static',
                        ...(viewOnly && { fontFamily: '"Times New Roman", Times, serif' }),
                        ...(viewOnly && { textAlign: 'center' }),
                      }
                    }}
                  >
                    {viewOnly ? (
                      <Typography 
                        variant="body2" 
                        className={viewOnly ? 'fontSet' : undefined}
                        sx={{ 
                          fontSize: viewOnly ? '9pt' : '0.65rem',
                          lineHeight: viewOnly ? '1.5' : '1.1',
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word',
                          overflowWrap: 'break-word',
                          margin: 0,
                          padding: 0,
                          fontFamily: viewOnly ? '"Times New Roman", Times, serif' : undefined,
                          '@media print': {
                            fontSize: viewOnly ? '9pt' : '0.65rem',
                            lineHeight: viewOnly ? '1.5' : '1.1',
                            fontFamily: viewOnly ? '"Times New Roman", Times, serif' : undefined,
                          }
                        }}
                      >
                        {rows[rowIndex]?.[col] || ''}
                      </Typography>
                    ) : (
                      <TextField
                        key={`cell-${rowIndex}-${col}`}
                        fullWidth
                        value={rows[rowIndex]?.[col] || ''}
                        onChange={(e) => {
                          e.stopPropagation();
                          const newValue = e.target.value;
                          handleCellChange(rowIndex, col, newValue);
                        }}
                        onKeyDown={(e) => {
                          e.stopPropagation();
                        }}
                        onKeyUp={(e) => {
                          e.stopPropagation();
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                        }}
                        size="small"
                        placeholder={colIndex === 0 ? 'Enter activities' : ''}
                        sx={{
                          '& .MuiInputBase-input': {
                            padding: '2px 3px',
                            fontSize: '0.7rem',
                            lineHeight: '1.2',
                          },
                          '& .MuiInputBase-root': {
                            minHeight: 'auto',
                          }
                        }}
                        multiline
                        rows={1}
                        autoFocus={false}
                      />
                    )}
                  </TableCell>
                ))}
                {!viewOnly && (
                  <TableCell
                    sx={{
                      position: 'sticky',
                      right: 0,
                      backgroundColor: 'white',
                      padding: '2px',
                      zIndex: 1,
                    }}
                  >
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteRow(rowIndex)}
                      sx={{ padding: '4px' }}
                      title="Delete Row"
                    >
                      <DeleteIcon fontSize="small" color="error" />
                    </IconButton>
                  </TableCell>
                )}
              </TableRow>
            ))}
            {rowIndices.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (viewOnly ? 0 : 1)}
                  align="center"
                  sx={{ padding: '20px', color: 'text.secondary' }}
                >
                  <Typography variant="body2">
                    No rows yet. Click "Add Row" to get started.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      {!viewOnly && (
        <FlexBox justifyContent="flex-start" marginTop="8px" gap="8px">
          <IconButton
            onClick={handleAddRow}
            color="primary"
            size="small"
            sx={{
              border: '1px solid',
              borderColor: 'primary.main',
              padding: '4px',
              '&:hover': {
                backgroundColor: 'primary.light',
                color: 'white',
              },
            }}
            title="Add Row"
          >
            <AddIcon fontSize="small" />
          </IconButton>
          <Typography variant="body2" sx={{ alignSelf: 'center', color: 'text.secondary', fontSize: '0.75rem' }}>
            Add Row
          </Typography>
        </FlexBox>
      )}
    </Box>
  );
};

// Memoize the component with custom comparison to prevent unnecessary re-renders
export default React.memo(EditableGanttTable, (prevProps, nextProps) => {
  // Only re-render if viewOnly or fieldKey changes, or if initialData actually changes
  if (prevProps.viewOnly !== nextProps.viewOnly) return false;
  if (prevProps.fieldKey !== nextProps.fieldKey) return false;
  
  // Deep compare initialData to prevent re-renders from formData updates
  const prevDataKeys = Object.keys(prevProps.initialData || {});
  const nextDataKeys = Object.keys(nextProps.initialData || {});
  
  if (prevDataKeys.length !== nextDataKeys.length) return false;
  
  // If component is already initialized, don't re-render on initialData changes
  // (This prevents focus loss when formData updates)
  return true; // Return true means "don't re-render" (props are equal)
});

