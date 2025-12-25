import { useState, useEffect } from "react";
import { Document, Page } from "react-pdf";

const LocalPDFViewer = ({ url }: { url: string }) => {
  const [pdfUrl, setPdfUrl] = useState<any>();

  useEffect(() => {
    const fetchPdfData = async () => {
      if (!url) return;

      try {
        const arrayBuffer = await fetch(url);
        const blob = await arrayBuffer.blob();
        const base64Url = await blobToURL(blob);
        setPdfUrl(base64Url);
      } catch (error) {}
    };

    fetchPdfData();
  }, [url]);

  // Utility to convert Blob to Base64
  const blobToURL = (blob: any) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = () => resolve(reader.result);
    });
  };

  return (
    <div>
      {pdfUrl ? (
        <Document file={pdfUrl}>
          <Page pageNumber={1} />
        </Document>
      ) : (
        <p>Loading PDF...</p>
      )}
    </div>
  );
};

export default LocalPDFViewer;
