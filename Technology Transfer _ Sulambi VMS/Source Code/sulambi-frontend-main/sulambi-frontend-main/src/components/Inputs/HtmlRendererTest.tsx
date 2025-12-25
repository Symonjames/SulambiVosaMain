import React from 'react';
import SafeHtmlRenderer from './SafeHtmlRenderer';

const HtmlRendererTest: React.FC = () => {
  const testHtmlContent = '<p><strong>hello joe, </strong><em>ultimatum est.</em></p>';
  const testCaption = '<strong>Bold caption</strong> with <em>italic text</em>';

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px' }}>
      <h3>HTML Renderer Test</h3>
      
      <div style={{ marginBottom: '20px' }}>
        <h4>Test HTML Content:</h4>
        <p><strong>Raw HTML:</strong> {testHtmlContent}</p>
        <p><strong>Rendered:</strong></p>
        <SafeHtmlRenderer htmlContent={testHtmlContent} />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h4>Test Caption:</h4>
        <p><strong>Raw HTML:</strong> {testCaption}</p>
        <p><strong>Rendered:</strong></p>
        <SafeHtmlRenderer htmlContent={testCaption} />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h4>Test with Styling:</h4>
        <SafeHtmlRenderer 
          htmlContent={testHtmlContent} 
          style={{ 
            border: '1px solid #ddd', 
            padding: '10px', 
            backgroundColor: '#f9f9f9',
            borderRadius: '4px'
          }} 
        />
      </div>
    </div>
  );
};

export default HtmlRendererTest;
