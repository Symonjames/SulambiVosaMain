# Import/Export Guidelines for Sulambi Frontend

## 🎯 Goal
Prevent recurring import/export errors that cause startup failures and module resolution issues.

## 📋 Rules

### 1. Default Exports for Components
**Always use default exports for React components:**

```tsx
// ✅ GOOD - Default export
const MyComponent: React.FC<Props> = ({ prop1, prop2 }) => {
  return <div>Content</div>;
};

export default MyComponent;
```

```tsx
// ❌ BAD - Named export (unless you have a specific reason)
export const MyComponent: React.FC<Props> = ({ prop1, prop2 }) => {
  return <div>Content</div>;
};
```

### 2. Default Imports for Components
**Always use default imports for React components:**

```tsx
// ✅ GOOD - Default import
import MyComponent from './MyComponent';
```

```tsx
// ❌ BAD - Named import for default-exported component
import { MyComponent } from './MyComponent';
```

### 3. Named Exports for Utilities
**Use named exports for utility functions, types, and constants:**

```tsx
// ✅ GOOD - Named exports for utilities
export const API_BASE_URL = 'http://localhost:8000/api';
export const formatDate = (date: Date) => { /* ... */ };
export type UserType = { id: number; name: string; };
```

```tsx
// ✅ GOOD - Named imports for utilities
import { API_BASE_URL, formatDate, UserType } from './utils';
```

### 4. File Naming Convention
- Components: `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- Utilities: `camelCase.ts` (e.g., `apiUtils.ts`)
- Types: `camelCase.ts` (e.g., `userTypes.ts`)

### 5. Clean File Endings
**Always end files with a single newline and no extra whitespace:**

```tsx
// ✅ GOOD
export default MyComponent;
```

```tsx
// ❌ BAD - Extra whitespace and multiple newlines
export default MyComponent;



```

## 🔧 Common Issues & Solutions

### Issue 1: "Module has no default export"
**Cause:** File has syntax errors or extra whitespace that breaks parsing.

**Solution:**
1. Check file syntax
2. Remove extra whitespace at end of file
3. Ensure proper export statement

### Issue 2: "The requested module does not provide an export named 'X'"
**Cause:** Importing a named export that doesn't exist, or importing default as named.

**Solution:**
1. Check if component uses default or named export
2. Match import type to export type
3. Use the export checker script

### Issue 3: Import/Export Mismatch
**Cause:** Inconsistent patterns across the codebase.

**Solution:**
1. Follow the guidelines above
2. Use the checker script: `node check-exports.js`
3. Fix any reported issues

## 🛠️ Tools

### Export Checker Script
Run this to check for export/import issues:

```bash
node check-exports.js
```

### TypeScript Build Check
Always test with TypeScript compilation:

```bash
npm run build
```

### Development Server
Test in development mode:

```bash
npm run dev
```

## 📝 Checklist Before Committing

- [ ] All components use default exports
- [ ] All component imports use default imports
- [ ] Utility functions use named exports
- [ ] No extra whitespace at end of files
- [ ] TypeScript build passes (`npm run build`)
- [ ] Development server starts without errors (`npm run dev`)
- [ ] Export checker script passes (`node check-exports.js`)

## 🚨 Emergency Fixes

If you encounter import/export errors:

1. **Quick Fix for Default Export Issues:**
   ```tsx
   // At end of component file
   export default ComponentName;
   ```

2. **Quick Fix for Import Issues:**
   ```tsx
   // For default-exported components
   import ComponentName from './ComponentName';
   
   // For named exports
   import { utilityFunction, TypeName } from './utils';
   ```

3. **File Cleanup:**
   ```bash
   # Remove extra whitespace from files
   find src -name "*.tsx" -o -name "*.ts" | xargs sed -i 's/[[:space:]]*$//'
   ```

## 🎯 Best Practices Summary

1. **Consistency is key** - Use the same pattern throughout the project
2. **Default exports for components** - Makes imports cleaner and more predictable
3. **Named exports for utilities** - Allows importing only what you need
4. **Clean file endings** - Prevents parsing issues
5. **Regular checks** - Use the tools provided to catch issues early
6. **TypeScript compliance** - Always ensure TypeScript compilation passes

Following these guidelines will prevent the recurring import/export headaches and ensure smooth project startup every time.






























































