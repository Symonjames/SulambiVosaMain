/**
 * Print fix utility specifically for External Report PDF
 * This reduces spacing in <ul> list items to match Internal Report
 */

export const applyExternalReportPrintFix = (container: HTMLElement): (() => void) => {
  if (!container) return () => {};

  // Function to reduce spacing in list items
  const reduceSpacing = () => {
    // Target all <ul> elements inside table cells
    const ulElements = container.querySelectorAll('td ul, th ul');
    ulElements.forEach((el) => {
      const htmlEl = el as HTMLElement;
      // Remove all margin and padding
      htmlEl.style.removeProperty('margin');
      htmlEl.style.removeProperty('margin-top');
      htmlEl.style.removeProperty('margin-bottom');
      htmlEl.style.removeProperty('padding');
      htmlEl.style.removeProperty('padding-top');
      htmlEl.style.removeProperty('padding-bottom');
      
      // Set minimal spacing with !important
      htmlEl.style.setProperty('margin-top', '1px', 'important');
      htmlEl.style.setProperty('margin-bottom', '1px', 'important');
      htmlEl.style.setProperty('padding-top', '0', 'important');
      htmlEl.style.setProperty('padding-bottom', '0', 'important');
    });

    // Target all <li> elements inside table cells
    const liElements = container.querySelectorAll('td ul li, th ul li');
    liElements.forEach((el) => {
      const htmlEl = el as HTMLElement;
      // Remove all margin and padding
      htmlEl.style.removeProperty('margin');
      htmlEl.style.removeProperty('margin-top');
      htmlEl.style.removeProperty('margin-bottom');
      htmlEl.style.removeProperty('padding');
      htmlEl.style.removeProperty('padding-top');
      htmlEl.style.removeProperty('padding-bottom');
      
      // Set minimal spacing with !important
      htmlEl.style.setProperty('margin-top', '0', 'important');
      htmlEl.style.setProperty('margin-bottom', '0', 'important');
      htmlEl.style.setProperty('padding-top', '0', 'important');
      htmlEl.style.setProperty('padding-bottom', '0', 'important');
      htmlEl.style.setProperty('line-height', '1.2', 'important');
    });
  };

  // Apply immediately
  reduceSpacing();

  // Apply multiple times to catch all elements
  setTimeout(reduceSpacing, 50);
  setTimeout(reduceSpacing, 100);
  setTimeout(reduceSpacing, 150);

  // Use MutationObserver to catch any style changes
  const observer = new MutationObserver(() => {
    reduceSpacing();
  });

  observer.observe(container, {
    attributes: true,
    attributeFilter: ['style', 'class'],
    subtree: true,
    childList: true,
  });

  // Store observer for cleanup
  (container as any).__externalReportPrintObserver = observer;

  // Return cleanup function
  return () => {
    observer.disconnect();
    delete (container as any).__externalReportPrintObserver;
  };
};

export const cleanupExternalReportPrintFix = (container: HTMLElement | null): void => {
  if (container && (container as any).__externalReportPrintObserver) {
    (container as any).__externalReportPrintObserver.disconnect();
    delete (container as any).__externalReportPrintObserver;
  }
};











