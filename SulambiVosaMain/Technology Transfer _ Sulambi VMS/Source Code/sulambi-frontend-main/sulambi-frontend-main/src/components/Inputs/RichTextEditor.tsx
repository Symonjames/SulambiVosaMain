import React, { useMemo } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { Box, Typography } from '@mui/material';
import FlexBox from '../FlexBox';

interface RichTextEditorProps {
  question: string;
  required?: boolean;
  value?: string;
  onChange?: (value: string) => void;
  error?: boolean;
  placeholder?: string;
  disabled?: boolean;
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({
  question,
  required = false,
  value = '',
  onChange,
  error = false,
  placeholder = '',
  disabled = false,
}) => {
  
  const modules = useMemo(() => ({
    toolbar: {
      container: [
        ['bold', 'italic', 'underline'],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        [{ 'align': [] }],
        [{ 'indent': '-1'}, { 'indent': '+1' }], // Indentation for tabs and spacing
      ],
    },
    keyboard: {
      bindings: {
        tab: {
          key: 'Tab',
          handler: function() {
            // Allow tab for indentation
            return true;
          }
        }
      }
    }
  }), []);

  const formats = [
    'bold', 'italic', 'underline',
    'list', 'bullet', 'indent',
    'align'
  ];

  return (
    <FlexBox width="100%" flexDirection="column">
      <Typography color={error ? "red" : "var(--text-landing)"} marginBottom="10px">
        {question}
        {required && <b style={{ color: "red" }}>*</b>}
      </Typography>
      <Box
        sx={{
          '& .ql-editor': {
            minHeight: '200px',
            fontSize: '10pt', // Font size 10
            fontFamily: '"Times New Roman", Times, serif', // Times New Roman font
            lineHeight: '1.6', // Default line spacing
            padding: '12px',
            '& p': {
              marginBottom: '8px',
              lineHeight: '1.6',
              fontSize: '10pt',
              fontFamily: '"Times New Roman", Times, serif',
              textAlign: 'justify',
              textIndent: '0',
            },
            '& ol, & ul': {
              marginBottom: '8px',
              lineHeight: '1.6',
              fontSize: '10pt',
              fontFamily: '"Times New Roman", Times, serif',
            },
            '& li': {
              marginBottom: '4px',
              lineHeight: '1.6',
              fontSize: '10pt',
              fontFamily: '"Times New Roman", Times, serif',
            },
            '& div': {
              textAlign: 'justify',
              textIndent: '0',
            },
          },
          '& .ql-toolbar': {
            borderTop: '1px solid #ccc',
            borderLeft: '1px solid #ccc',
            borderRight: '1px solid #ccc',
            borderTopLeftRadius: '4px',
            borderTopRightRadius: '4px',
            backgroundColor: '#fafafa',
          },
          '& .ql-container': {
            borderBottom: '1px solid #ccc',
            borderLeft: '1px solid #ccc',
            borderRight: '1px solid #ccc',
            borderBottomLeftRadius: '4px',
            borderBottomRightRadius: '4px',
            fontSize: '10pt',
            fontFamily: '"Times New Roman", Times, serif',
            ...(error && {
              borderColor: 'red',
            }),
          },
          '& .ql-editor.ql-blank::before': {
            fontStyle: 'normal',
            color: '#999',
            fontSize: '10pt',
            fontFamily: '"Times New Roman", Times, serif',
          },
          // Table styles
          '& .ql-editor table': {
            borderCollapse: 'collapse',
            width: '100%',
            margin: '10px 0',
            '& td, & th': {
              border: '1px solid #ccc',
              padding: '8px',
              minWidth: '50px',
            },
            '& th': {
              backgroundColor: '#f5f5f5',
              fontWeight: 'bold',
            },
          },
        }}
      >
        <ReactQuill
          theme="snow"
          value={value}
          onChange={onChange}
          modules={modules}
          formats={formats}
          placeholder={placeholder}
          readOnly={disabled}
        />
      </Box>
    </FlexBox>
  );
};

export default RichTextEditor;
