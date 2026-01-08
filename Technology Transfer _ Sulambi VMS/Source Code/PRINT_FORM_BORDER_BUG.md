# Print Form Border Container Bug Report

## Bug Description

**Component:** Frontend - Print Form Styling  
**Feature:** BSU Form Tables (bsuForm/bsuFormChild)  
**Severity:** High  
**Date:** [Current Date]

### Symptoms
- When zooming in/out on print forms, the border container disappears
- The outer border of `table.bsuForm` and `table.bsuFormChild` elements is missing at certain zoom levels
- Borders may appear at 100% zoom but disappear at other zoom levels (e.g., 75%, 125%, 150%)
- This affects the visual appearance and print quality of forms

### Steps to Reproduce
1. Open a page with BSU form tables (e.g., Event Proposal form)
2. View the form in print preview or print view
3. Zoom in/out using browser zoom (Ctrl/Cmd + Plus/Minus) or print preview zoom
4. Observe that the outer border container disappears at certain zoom levels
5. Check at zoom levels: 50%, 75%, 100%, 125%, 150%, 200%

### Root Cause Analysis

**Likely Causes:**
1. **Sub-pixel border rendering**: At non-100% zoom, `1px` borders may render as sub-pixels, causing browsers to not display them
2. **Missing `!important` flags**: Some border styles in print media queries may not have `!important`, allowing them to be overridden
3. **Border-collapse issues**: `border-collapse: collapse` combined with zoom may cause border rendering issues
4. **Box-sizing conflicts**: `box-sizing: border-box` at different zoom levels may affect border visibility
5. **Browser rendering engine**: Different browsers handle border rendering at zoom levels differently

**Affected CSS Classes:**
- `table.bsuForm` - Main form table with `border: 1px solid black`
- `table.bsuFormChild` - Child form tables with `border: 1px solid black`
- `.bsu-form-wrapper` - Wrapper container

### Current CSS (Problematic)

```css
table.bsuForm {
  border: 1px solid black;  /* May disappear at zoom */
}

table.bsuFormChild {
  border: 1px solid black;  /* May disappear at zoom */
  border-top: none;
}
```

### Expected Behavior
- Borders should remain visible at ALL zoom levels (50% to 200%)
- Borders should render consistently in both screen and print views
- Border thickness should scale appropriately with zoom
- No visual gaps or missing borders at any zoom level

### Impact
- **User Experience**: Forms look incomplete or unprofessional
- **Print Quality**: Printed forms may be missing borders
- **Accessibility**: Visual structure is lost, making forms harder to read
- **Compliance**: May not meet document formatting requirements

---

## Logging Implementation

### Step 2: Add Logging

We need to add logging to track:
1. Current zoom level
2. Border computed styles at different zoom levels
3. Browser rendering behavior
4. CSS rule application

### Logging Code

Add this to a component that renders print forms or create a utility hook:

```typescript
// utils/printFormBorderLogger.ts
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
    allBordersVisible: parseFloat(borderTop) > 0 && 
                       parseFloat(borderRight) > 0 && 
                       parseFloat(borderBottom) > 0 && 
                       parseFloat(borderLeft) > 0
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
};

export const logAllFormBorders = (container: HTMLElement | null, zoomLevel: number) => {
  if (!container) {
    console.warn('[PRINT_FORM_BORDER] Container not found');
    return;
  }

  const bsuForms = container.querySelectorAll('table.bsuForm');
  const bsuFormChildren = container.querySelectorAll('table.bsuFormChild');

  console.log(`[PRINT_FORM_BORDER] Found ${bsuForms.length} bsuForm tables and ${bsuFormChildren.length} bsuFormChild tables at ${zoomLevel}% zoom`);

  bsuForms.forEach((form, index) => {
    console.log(`[PRINT_FORM_BORDER] Checking bsuForm #${index + 1}`);
    logBorderStyles(form as HTMLElement, zoomLevel);
  });

  bsuFormChildren.forEach((form, index) => {
    console.log(`[PRINT_FORM_BORDER] Checking bsuFormChild #${index + 1}`);
    logBorderStyles(form as HTMLElement, zoomLevel);
  });
};

// Hook to track zoom changes
export const useZoomTracker = (containerRef: React.RefObject<HTMLElement>) => {
  useEffect(() => {
    const checkZoom = () => {
      const zoomLevel = Math.round((window.outerWidth / window.innerWidth) * 100);
      // Or use: const zoomLevel = Math.round((screen.width / window.innerWidth) * 100);
      
      console.log('[PRINT_FORM_BORDER] Zoom level changed', { zoomLevel: `${zoomLevel}%` });
      
      if (containerRef.current) {
        logAllFormBorders(containerRef.current, zoomLevel);
      }
    };

    // Check on mount
    checkZoom();

    // Listen for resize (zoom changes trigger resize)
    window.addEventListener('resize', checkZoom);
    
    // Also listen for print preview
    window.addEventListener('beforeprint', () => {
      console.log('[PRINT_FORM_BORDER] Print preview opened');
      setTimeout(checkZoom, 100); // Small delay to let print styles apply
    });

    window.addEventListener('afterprint', () => {
      console.log('[PRINT_FORM_BORDER] Print preview closed');
      setTimeout(checkZoom, 100);
    });

    return () => {
      window.removeEventListener('resize', checkZoom);
      window.removeEventListener('beforeprint', checkZoom);
      window.removeEventListener('afterprint', checkZoom);
    };
  }, [containerRef]);
};
```

---

## Step 3: Expected Logs

### Expected Log Flow at 100% Zoom

```
[PRINT_FORM_BORDER] Zoom level changed { zoomLevel: "100%" }
[PRINT_FORM_BORDER] Found 2 bsuForm tables and 5 bsuFormChild tables at 100% zoom
[PRINT_FORM_BORDER] Checking bsuForm #1
[PRINT_FORM_BORDER] Border Styles Check {
  zoomLevel: "100%",
  element: "TABLE",
  className: "bsuForm",
  borderTop: "1px solid rgb(0, 0, 0)",
  borderRight: "1px solid rgb(0, 0, 0)",
  borderBottom: "1px solid rgb(0, 0, 0)",
  borderLeft: "1px solid rgb(0, 0, 0)",
  borderCollapse: "collapse",
  boxSizing: "border-box",
  allBordersVisible: true
}
[PRINT_FORM_BORDER] Element Bounds {
  zoomLevel: "100%",
  width: 800,
  height: 200,
  borderVisible: true
}
```

### Expected Log Flow at 75% Zoom (Problematic)

```
[PRINT_FORM_BORDER] Zoom level changed { zoomLevel: "75%" }
[PRINT_FORM_BORDER] Found 2 bsuForm tables and 5 bsuFormChild tables at 75% zoom
[PRINT_FORM_BORDER] Checking bsuForm #1
[PRINT_FORM_BORDER] Border Styles Check {
  zoomLevel: "75%",
  element: "TABLE",
  className: "bsuForm",
  borderTop: "0.75px solid rgb(0, 0, 0)",  // ⚠️ Sub-pixel border
  borderRight: "0.75px solid rgb(0, 0, 0)",  // ⚠️ May not render
  borderBottom: "0.75px solid rgb(0, 0, 0)",  // ⚠️ May not render
  borderLeft: "0.75px solid rgb(0, 0, 0)",  // ⚠️ May not render
  allBordersVisible: false  // ❌ PROBLEM: Borders computed but not visible
}
```

### Expected Log Flow at 125% Zoom (Problematic)

```
[PRINT_FORM_BORDER] Zoom level changed { zoomLevel: "125%" }
[PRINT_FORM_BORDER] Border Styles Check {
  zoomLevel: "125%",
  borderTop: "1.25px solid rgb(0, 0, 0)",  // ⚠️ Sub-pixel border
  allBordersVisible: false  // ❌ PROBLEM: May render inconsistently
}
```

---

## Step 4: Actual Logs (To Be Captured)

**Instructions:**
1. Add the logging code to your print form component
2. Open browser console (F12)
3. Navigate to a page with print forms
4. Zoom to different levels: 50%, 75%, 100%, 125%, 150%, 200%
5. Copy all console logs starting with `[PRINT_FORM_BORDER]`
6. Paste logs here:

```
[PASTE ACTUAL LOGS HERE]
```

---

## Step 5: Fix Implementation

### Proposed CSS Fix

The fix should ensure borders are always visible at any zoom level:

```css
/* Force minimum border width to prevent sub-pixel rendering issues */
table.bsuForm {
  border: 1px solid black !important;
  border-width: 1px !important;
  min-width: 1px; /* Ensure border is always at least 1px */
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

table.bsuFormChild {
  border: 1px solid black !important;
  border-width: 1px !important;
  border-top: none;
  min-width: 1px;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* Ensure borders at all zoom levels in print */
@media print {
  table.bsuForm,
  table.bsuFormChild {
    border: 1px solid #000 !important;
    border-width: 1px !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    /* Force border rendering */
    outline: 1px solid #000;
    outline-offset: -1px;
  }
  
  /* Alternative: Use box-shadow as fallback for borders */
  table.bsuForm,
  table.bsuFormChild {
    box-shadow: inset 0 0 0 1px #000 !important;
  }
}
```

---

## Testing Checklist

After implementing the fix:

- [ ] Test at 50% zoom - borders visible
- [ ] Test at 75% zoom - borders visible
- [ ] Test at 100% zoom - borders visible
- [ ] Test at 125% zoom - borders visible
- [ ] Test at 150% zoom - borders visible
- [ ] Test at 200% zoom - borders visible
- [ ] Test in print preview - borders visible
- [ ] Test actual print - borders print correctly
- [ ] Test in Chrome - borders visible
- [ ] Test in Firefox - borders visible
- [ ] Test in Edge - borders visible
- [ ] Verify logs show `allBordersVisible: true` at all zoom levels

---

**Status:** 🔴 Bug Identified - Awaiting Logs  
**Next Steps:** 
1. Add logging code
2. Capture logs at different zoom levels
3. Analyze logs to confirm root cause
4. Implement CSS fix
5. Verify fix with logs












