/**
 * Standard Print Fix Utility
 * Applies consistent formatting to all form types for printing
 */

export const applyStandardPrintFix = (container: HTMLElement | null): (() => void) => {
  if (!container) return () => {};

  // Apply standard formatting to all form elements
  const applyFormatting = () => {
    if (!container) return;

    // Standardize table cells - preserve existing padding if set
    const cells = container.querySelectorAll('td, th');
    cells.forEach((cell) => {
      const htmlCell = cell as HTMLElement;
      // Only set default padding if not already set by component
      if (!htmlCell.style.padding || htmlCell.style.padding === '0px' || htmlCell.style.padding === '') {
        htmlCell.style.setProperty('padding', '6px 8px', 'important');
      }
      // Remove excessive margins
      htmlCell.style.setProperty('margin', '0', 'important');
    });

    // Standardize table spacing - but preserve FinancialPlanTable width
    const tables = container.querySelectorAll('table.bsuForm, table.bsuFormChild');
    tables.forEach((table) => {
      const htmlTable = table as HTMLElement;
      // Preserve FinancialPlanTable fixed width (420px)
      if (htmlTable.classList.contains('financial-plan')) {
        htmlTable.style.setProperty('width', '420px', 'important');
        htmlTable.style.setProperty('max-width', '420px', 'important');
        htmlTable.style.setProperty('margin', '0 auto', 'important');
      } else {
        htmlTable.style.setProperty('width', '100%', 'important');
        htmlTable.style.setProperty('max-width', '100%', 'important');
      }
      // Only remove margins if not explicitly set
      if (!htmlTable.style.marginTop || htmlTable.style.marginTop === '0px') {
        htmlTable.style.setProperty('margin-top', '0', 'important');
      }
      if (!htmlTable.style.marginBottom || htmlTable.style.marginBottom === '0px') {
        htmlTable.style.setProperty('margin-bottom', '0', 'important');
      }
      htmlTable.style.setProperty('border-collapse', 'collapse', 'important');
    });

    // Preserve Roman list items styling (don't override if already set)
    const romanListItems = container.querySelectorAll('.roman-list-item');
    romanListItems.forEach((item) => {
      const htmlItem = item as HTMLElement;
      // Only set defaults if not already set by component
      if (!htmlItem.style.marginTop || htmlItem.style.marginTop === '0px') {
        // Preserve component's margin (typically 10px)
        htmlItem.style.setProperty('margin-top', '10px', 'important');
      }
      if (!htmlItem.style.marginBottom || htmlItem.style.marginBottom === '0px') {
        htmlItem.style.setProperty('margin-bottom', '10px', 'important');
      }
      if (!htmlItem.style.lineHeight || htmlItem.style.lineHeight === 'normal') {
        htmlItem.style.setProperty('line-height', '1.5', 'important');
      }
      if (!htmlItem.style.paddingLeft || htmlItem.style.paddingLeft === '0px') {
        htmlItem.style.setProperty('padding-left', '2.5em', 'important');
      }
    });
    
    // Standardize other list items (ul, ol li)
    const listItems = container.querySelectorAll('li:not(.roman-list-item)');
    listItems.forEach((item) => {
      const htmlItem = item as HTMLElement;
      // Only apply if not in a Roman list item
      if (!htmlItem.closest('.roman-list-item')) {
        htmlItem.style.setProperty('margin-top', '2px', 'important');
        htmlItem.style.setProperty('margin-bottom', '2px', 'important');
        htmlItem.style.setProperty('line-height', '1.3', 'important');
      }
    });

    // Standardize lists (ul, ol)
    const lists = container.querySelectorAll('ul, ol');
    lists.forEach((list) => {
      const htmlList = list as HTMLElement;
      htmlList.style.setProperty('margin-top', '2px', 'important');
      htmlList.style.setProperty('margin-bottom', '2px', 'important');
      htmlList.style.setProperty('padding-left', '1.5em', 'important');
    });

    // Standardize divs with fontSet class
    const fontSetDivs = container.querySelectorAll('.fontSet > div, .fontSet');
    fontSetDivs.forEach((div) => {
      const htmlDiv = div as HTMLElement;
      // Only apply if no explicit margin is set
      if (!htmlDiv.style.margin || htmlDiv.style.margin === '0px') {
        htmlDiv.style.setProperty('margin-top', '2px', 'important');
        htmlDiv.style.setProperty('margin-bottom', '2px', 'important');
      }
    });

    // Standardize header content group
    const headerGroups = container.querySelectorAll('.header-content-group');
    headerGroups.forEach((group) => {
      const htmlGroup = group as HTMLElement;
      htmlGroup.style.setProperty('margin', '0', 'important');
      htmlGroup.style.setProperty('padding', '0', 'important');
      htmlGroup.style.setProperty('display', 'block', 'important');
    });

    // Standardize bsu-form-wrapper
    const formWrappers = container.querySelectorAll('.bsu-form-wrapper');
    formWrappers.forEach((wrapper) => {
      const htmlWrapper = wrapper as HTMLElement;
      htmlWrapper.style.setProperty('margin', '0', 'important');
      htmlWrapper.style.setProperty('padding', '0', 'important');
    });

    // Remove excessive spacing from table rows
    const rows = container.querySelectorAll('tr');
    rows.forEach((row) => {
      const htmlRow = row as HTMLElement;
      htmlRow.style.setProperty('margin', '0', 'important');
      htmlRow.style.setProperty('padding', '0', 'important');
    });

    // Standardize images
    const images = container.querySelectorAll('img');
    images.forEach((img) => {
      const htmlImg = img as HTMLElement;
      htmlImg.style.setProperty('max-width', '100%', 'important');
      htmlImg.style.setProperty('height', 'auto', 'important');
    });
  };

  // Apply formatting immediately
  applyFormatting();

  // Apply formatting again after a short delay to catch any React re-renders
  const timeoutId = setTimeout(applyFormatting, 100);

  // Return cleanup function
  return () => {
    clearTimeout(timeoutId);
  };
};

export const cleanupStandardPrintFix = (_container: HTMLElement | null): void => {
  // Cleanup is handled by removing the container, so this is a no-op
  // but kept for consistency with other print fix utilities
  // The underscore prefix indicates this parameter is intentionally unused
};

