/**
 * Print Form Border Logger
 * 
 * This utility logs border styles and visibility at different zoom levels
 * to help debug the border container disappearing issue.
 */

/**
 * Log border styles for a single element
 */
export const logBorderStyles = (element: HTMLElement | null, zoomLevel: number) => {
  if (!element) {
    console.warn('[PRINT_FORM_BORDER] Element not found');
    return;
  }

  const computedStyle = window.getComputedStyle(element);
  const borderTop = computedStyle.borderTopWidth;
  const borderRight = computedStyle.borderRightWidth;
  const borderBottom = computedStyle.borderBottomWidth;
  const borderLeft = computedStyle.borderLeftWidth;
  const borderColor = computedStyle.borderColor;
  const borderStyle = computedStyle.borderStyle;
  const borderCollapse = computedStyle.borderCollapse;
  const boxSizing = computedStyle.boxSizing;
  const width = computedStyle.width;
  const height = computedStyle.height;

  const allBordersVisible = 
    parseFloat(borderTop) > 0 && 
    parseFloat(borderRight) > 0 && 
    parseFloat(borderBottom) > 0 && 
    parseFloat(borderLeft) > 0;

  console.log('[PRINT_FORM_BORDER] Border Styles Check', {
    zoomLevel: `${zoomLevel}%`,
    element: element.tagName,
    className: element.className,
    borderTop: `${borderTop} ${borderStyle} ${borderColor}`,
    borderRight: `${borderRight} ${borderStyle} ${borderColor}`,
    borderBottom: `${borderBottom} ${borderStyle} ${borderColor}`,
    borderLeft: `${borderLeft} ${borderStyle} ${borderColor}`,
    borderCollapse,
    boxSizing,
    dimensions: `${width} x ${height}`,
    allBordersVisible,
    borderTopValue: parseFloat(borderTop),
    borderRightValue: parseFloat(borderRight),
    borderBottomValue: parseFloat(borderBottom),
    borderLeftValue: parseFloat(borderLeft)
  });

  // Check if borders are actually visible
  const rect = element.getBoundingClientRect();
  console.log('[PRINT_FORM_BORDER] Element Bounds', {
    zoomLevel: `${zoomLevel}%`,
    x: rect.x,
    y: rect.y,
    width: rect.width,
    height: rect.height,
    borderVisible: rect.width > 0 && rect.height > 0
  });

  // Visual check - try to detect if border is actually rendered
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (ctx) {
    // This is a simplified check - actual border detection would require more complex logic
    console.log('[PRINT_FORM_BORDER] Border Visibility Check', {
      zoomLevel: `${zoomLevel}%`,
      computedBorderWidth: borderTop,
      isSubPixel: parseFloat(borderTop) < 1 && parseFloat(borderTop) > 0,
      warning: parseFloat(borderTop) < 1 ? '⚠️ Sub-pixel border may not render!' : '✅ Border should render'
    });
  }

  return {
    allBordersVisible,
    borderTop: parseFloat(borderTop),
    borderRight: parseFloat(borderRight),
    borderBottom: parseFloat(borderBottom),
    borderLeft: parseFloat(borderLeft),
    isSubPixel: parseFloat(borderTop) < 1 && parseFloat(borderTop) > 0
  };
};

/**
 * Log all form borders in a container
 */
export const logAllFormBorders = (container: HTMLElement | null, zoomLevel: number) => {
  if (!container) {
    console.warn('[PRINT_FORM_BORDER] Container not found');
    return;
  }

  const bsuForms = container.querySelectorAll('table.bsuForm');
  const bsuFormChildren = container.querySelectorAll('table.bsuFormChild');

  console.log(`[PRINT_FORM_BORDER] ========================================`);
  console.log(`[PRINT_FORM_BORDER] Zoom Level: ${zoomLevel}%`);
  console.log(`[PRINT_FORM_BORDER] Found ${bsuForms.length} bsuForm tables`);
  console.log(`[PRINT_FORM_BORDER] Found ${bsuFormChildren.length} bsuFormChild tables`);
  console.log(`[PRINT_FORM_BORDER] ========================================`);

  const results: Array<{ element: HTMLElement; result: ReturnType<typeof logBorderStyles> }> = [];

  bsuForms.forEach((form, index) => {
    console.log(`[PRINT_FORM_BORDER] --- Checking bsuForm #${index + 1} ---`);
    const result = logBorderStyles(form as HTMLElement, zoomLevel);
    results.push({ element: form as HTMLElement, result: result! });
  });

  bsuFormChildren.forEach((form, index) => {
    console.log(`[PRINT_FORM_BORDER] --- Checking bsuFormChild #${index + 1} ---`);
    const result = logBorderStyles(form as HTMLElement, zoomLevel);
    results.push({ element: form as HTMLElement, result: result! });
  });

  // Summary
  const allVisible = results.every(r => r.result?.allBordersVisible);
  const hasSubPixel = results.some(r => r.result?.isSubPixel);
  
  console.log(`[PRINT_FORM_BORDER] ========================================`);
  console.log(`[PRINT_FORM_BORDER] SUMMARY at ${zoomLevel}% zoom:`);
  console.log(`[PRINT_FORM_BORDER] All borders visible: ${allVisible ? '✅ YES' : '❌ NO'}`);
  console.log(`[PRINT_FORM_BORDER] Sub-pixel borders detected: ${hasSubPixel ? '⚠️ YES' : '✅ NO'}`);
  console.log(`[PRINT_FORM_BORDER] ========================================`);

  return results;
};

/**
 * Get current zoom level
 */
export const getZoomLevel = (): number => {
  // Method 1: Using device pixel ratio
  const dpr = window.devicePixelRatio || 1;
  
  // Method 2: Using screen dimensions (more accurate for browser zoom)
  const screenWidth = screen.width;
  const windowWidth = window.innerWidth;
  const zoomByScreen = Math.round((screenWidth / windowWidth) * 100);
  
  // Method 3: Using outer/inner width ratio
  const zoomByOuter = Math.round((window.outerWidth / window.innerWidth) * 100);
  
  // Use the most reliable method
  // For browser zoom, screen method is usually most accurate
  return zoomByScreen || zoomByOuter || 100;
};

/**
 * React hook to track zoom changes and log border styles
 */
import { useEffect, useRef } from 'react';

export const useZoomTracker = (containerRef: React.RefObject<HTMLElement>, enabled: boolean = true) => {
  const lastZoomLevel = useRef<number>(100);

  useEffect(() => {
    if (!enabled) return;

    const checkZoom = () => {
      const currentZoom = getZoomLevel();
      
      // Only log if zoom changed significantly (more than 1%)
      if (Math.abs(currentZoom - lastZoomLevel.current) > 1) {
        console.log('[PRINT_FORM_BORDER] Zoom level changed', { 
          previousZoom: `${lastZoomLevel.current}%`,
          currentZoom: `${currentZoom}%`,
          change: `${currentZoom - lastZoomLevel.current > 0 ? '+' : ''}${currentZoom - lastZoomLevel.current}%`
        });
        
        lastZoomLevel.current = currentZoom;
        
        if (containerRef.current) {
          // Small delay to ensure styles are applied
          setTimeout(() => {
            logAllFormBorders(containerRef.current, currentZoom);
          }, 100);
        }
      }
    };

    // Check on mount
    const initialZoom = getZoomLevel();
    lastZoomLevel.current = initialZoom;
    console.log('[PRINT_FORM_BORDER] Initial zoom level:', { zoomLevel: `${initialZoom}%` });
    
    if (containerRef.current) {
      setTimeout(() => {
        logAllFormBorders(containerRef.current, initialZoom);
      }, 500);
    }

    // Listen for resize (zoom changes trigger resize)
    window.addEventListener('resize', checkZoom);
    
    // Also listen for print preview - store references for cleanup
    const handleBeforePrint = () => {
      console.log('[PRINT_FORM_BORDER] Print preview opened');
      const zoom = getZoomLevel();
      setTimeout(() => {
        if (containerRef.current) {
          logAllFormBorders(containerRef.current, zoom);
        }
      }, 200); // Longer delay for print styles to apply
    };

    const handleAfterPrint = () => {
      console.log('[PRINT_FORM_BORDER] Print preview closed');
      const zoom = getZoomLevel();
      setTimeout(() => {
        if (containerRef.current) {
          logAllFormBorders(containerRef.current, zoom);
        }
      }, 200);
    };

    window.addEventListener('beforeprint', handleBeforePrint);
    window.addEventListener('afterprint', handleAfterPrint);

    // Periodic check (in case zoom detection doesn't work via resize)
    const intervalId = setInterval(() => {
      checkZoom();
    }, 1000);

    return () => {
      window.removeEventListener('resize', checkZoom);
      window.removeEventListener('beforeprint', handleBeforePrint);
      window.removeEventListener('afterprint', handleAfterPrint);
      clearInterval(intervalId);
    };
  }, [containerRef, enabled]);
};

/**
 * Manual trigger function for testing
 */
export const triggerBorderLog = (container: HTMLElement | null) => {
  const zoom = getZoomLevel();
  console.log('[PRINT_FORM_BORDER] Manual trigger at zoom:', `${zoom}%`);
  logAllFormBorders(container, zoom);
};












