import React, { useEffect } from 'react';
import DOMPurify from 'dompurify';

interface SafeHtmlRendererProps {
  htmlContent: string;
  className?: string;
  style?: React.CSSProperties;
  allowedTags?: string[];
  allowedAttributes?: string[];
}

const SafeHtmlRenderer: React.FC<SafeHtmlRendererProps> = ({
  htmlContent,
  className,
  style,
  allowedTags = ['p', 'strong', 'em', 'u', 'b', 'i', 'br', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'div', 'span', 'blockquote', 'pre', 'code'],
  allowedAttributes = ['class', 'style', 'colspan', 'rowspan', 'align']
}) => {
  // Default configuration for DOMPurify
  const defaultConfig = {
    ALLOWED_TAGS: allowedTags,
    ALLOWED_ATTR: allowedAttributes,
    ALLOW_DATA_ATTR: false,
    ALLOW_UNKNOWN_PROTOCOLS: false,
    SANITIZE_DOM: true,
    KEEP_CONTENT: true,
    RETURN_DOM: false,
    RETURN_DOM_FRAGMENT: false,
    RETURN_DOM_IMPORT: false,
    RETURN_TRUSTED_TYPE: false,
    FORBID_TAGS: ['script', 'object', 'embed', 'link', 'meta', 'iframe', 'form', 'input', 'button'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur', 'onchange', 'onsubmit']
  };

  // Sanitize the HTML content
  const sanitizedHtml = DOMPurify.sanitize(htmlContent || '', defaultConfig);

  // If content is empty or only whitespace, return empty div
  if (!sanitizedHtml || sanitizedHtml.trim() === '') {
    return <div className={className} style={style} />;
  }

  // Default style with Times New Roman and 10pt font, justified text with first-line indentation
  const defaultStyle: React.CSSProperties = {
    fontFamily: '"Times New Roman", Times, serif',
    fontSize: '10pt',
    lineHeight: '1.6',
    textAlign: 'justify',
    ...style,
  };
  
  // Add CSS for paragraph indentation
  useEffect(() => {
    if (!document.head.querySelector('style[data-safe-html-renderer]')) {
      const styleTag = document.createElement('style');
      styleTag.setAttribute('data-safe-html-renderer', 'true');
      styleTag.textContent = `
        /* Force Times New Roman 10pt everywhere inside the renderer */
        .safe-html-renderer, 
        .safe-html-renderer * {
          font-family: "Times New Roman", Times, serif !important;
          font-size: 10pt !important;
          line-height: 1.6 !important;
        }
        .safe-html-renderer p,
        .safe-html-renderer div {
          text-align: justify !important;
          text-indent: 0 !important;
          margin: 0 !important;
          padding: 0 !important;
        }
        .safe-html-renderer table {
          margin-left: 0 !important;
          margin-right: 0 !important;
        }
      `;
      document.head.appendChild(styleTag);
    }
  }, []);

  return (
    <div 
      className={`safe-html-renderer ${className || ''}`}
      style={defaultStyle}
      dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
    />
  );
};

export default SafeHtmlRenderer;
