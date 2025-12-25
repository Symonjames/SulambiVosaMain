#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Function to check if a file has proper default export
function checkDefaultExport(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Check if file has default export
    const hasDefaultExport = /export\s+default\s+\w+;?\s*$/.test(content.trim());
    
    // Check if file is being imported as default elsewhere
    const fileName = path.basename(filePath, '.tsx');
    const searchPattern = new RegExp(`import\\s+${fileName}\\s+from`, 'g');
    
    return {
      file: filePath,
      hasDefaultExport,
      fileName
    };
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error.message);
    return null;
  }
}

// Function to find all imports of a component
function findImports(componentName, srcDir) {
  const imports = [];
  
  function searchDirectory(dir) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory() && file !== 'node_modules') {
        searchDirectory(filePath);
      } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
        try {
          const content = fs.readFileSync(filePath, 'utf8');
          if (content.includes(`import ${componentName}`)) {
            imports.push(filePath);
          }
        } catch (error) {
          // Ignore read errors
        }
      }
    });
  }
  
  searchDirectory(srcDir);
  return imports;
}

// Main function
function main() {
  const srcDir = path.join(__dirname, 'src');
  const componentsDir = path.join(srcDir, 'components', 'Forms');
  
  console.log('🔍 Checking export/import consistency...\n');
  
  if (!fs.existsSync(componentsDir)) {
    console.log('❌ Components directory not found');
    return;
  }
  
  const files = fs.readdirSync(componentsDir);
  const tsxFiles = files.filter(file => file.endsWith('.tsx'));
  
  let hasIssues = false;
  
  tsxFiles.forEach(file => {
    const filePath = path.join(componentsDir, file);
    const result = checkDefaultExport(filePath);
    
    if (result) {
      const componentName = result.fileName;
      const imports = findImports(componentName, srcDir);
      
      console.log(`📄 ${componentName}`);
      console.log(`   Export: ${result.hasDefaultExport ? '✅ Default export found' : '❌ No default export'}`);
      console.log(`   Imports: ${imports.length} files importing this component`);
      
      if (!result.hasDefaultExport && imports.length > 0) {
        console.log(`   ⚠️  WARNING: Component is imported but has no default export!`);
        console.log(`   Imported in:`);
        imports.forEach(imp => console.log(`     - ${imp}`));
        hasIssues = true;
      }
      
      console.log('');
    }
  });
  
  if (!hasIssues) {
    console.log('✅ All exports/imports look good!');
  } else {
    console.log('❌ Found export/import issues that need to be fixed.');
    process.exit(1);
  }
}

main();
