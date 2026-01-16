#!/usr/bin/env python3
"""
Update frontend image references to use Cloudinary URLs
This script:
1. Reads the cloudinary_migration_mapping.json file
2. Searches frontend code files for hardcoded image paths
3. Replaces local paths (uploads/...) with Cloudinary URLs
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Paths
FRONTEND_DIR = Path(__file__).parent
# Try to find mapping file - check backend directory
BACKEND_DIR = Path(__file__).parent.parent.parent / "sulambi-backend-main" / "sulambi-backend-main"
MAPPING_FILE = BACKEND_DIR / "cloudinary_migration_mapping.json"

# If not found, try alternative location (relative to backend root)
if not MAPPING_FILE.exists():
    # Try in current directory
    alt_path = Path("cloudinary_migration_mapping.json")
    if alt_path.exists():
        MAPPING_FILE = alt_path

# File extensions to search
FILE_EXTENSIONS = ['.tsx', '.ts', '.jsx', '.js', '.json']

# Patterns to match image paths
IMAGE_PATTERNS = [
    r'["\']uploads[/\\][^"\']+["\']',  # "uploads/file.jpg" or 'uploads/file.jpg'
    r'["\']/uploads/[^"\']+["\']',     # "/uploads/file.jpg"
    r'uploads[/\\][^"\s\'")]+',        # uploads/file.jpg (without quotes)
    r'/uploads/[^"\s\'")]+',           # /uploads/file.jpg (without quotes)
]

def load_mapping_file() -> Dict[str, str]:
    """Load the Cloudinary migration mapping file (JSONL format)"""
    if not MAPPING_FILE.exists():
        print(f"[ERROR] Mapping file not found: {MAPPING_FILE}")
        print("[INFO] Please run migrate_uploads_to_cloudinary.py first")
        return {}
    
    try:
        mapping = {}
        
        # The mapping file is JSONL (one JSON object per line)
        with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if 'old_value' in entry and 'new_value' in entry:
                        old_value = entry['old_value']
                        new_value = entry['new_value']
                        
                        # Extract filename from old_value (handles various formats)
                        old_path = old_value
                        # Remove uploads/ prefix if present
                        if 'uploads/' in old_path:
                            filename = old_path.split('uploads/')[-1].replace('\\', '/')
                        elif 'uploads\\' in old_path:
                            filename = old_path.split('uploads\\')[-1].replace('\\', '/')
                        else:
                            filename = old_path.replace('\\', '/')
                        
                        # Store multiple variations for lookup
                        mapping[filename] = new_value
                        mapping[f"uploads/{filename}"] = new_value
                        mapping[f"uploads\\{filename}"] = new_value
                        mapping[f"/uploads/{filename}"] = new_value
                        mapping[old_path] = new_value
                except json.JSONDecodeError:
                    continue
        
        print(f"[OK] Loaded {len(mapping)} image mappings from {MAPPING_FILE}")
        return mapping
    except Exception as e:
        print(f"[ERROR] Failed to load mapping file: {e}")
        return {}

def find_image_references(content: str, filename: str) -> List[Tuple[int, str, str]]:
    """
    Find all image path references in content
    Returns list of (line_number, original_match, normalized_path)
    """
    references = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Check all patterns
        for pattern in IMAGE_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                original = match.group(0)
                
                # Extract the path (remove quotes)
                path = original.strip('"\'').strip()
                
                # Normalize path for lookup
                normalized = path.replace('\\', '/')
                if normalized.startswith('/uploads/'):
                    normalized = normalized[1:]  # Remove leading /
                if normalized.startswith('uploads/'):
                    normalized = normalized.replace('uploads/', '', 1)
                
                references.append((line_num, original, normalized))
    
    return references

def replace_image_paths(content: str, mapping: Dict[str, str], file_path: Path) -> Tuple[str, int]:
    """
    Replace image paths with Cloudinary URLs
    Returns (updated_content, replacement_count)
    """
    if not mapping:
        return content, 0
    
    lines = content.split('\n')
    updated_lines = []
    replacement_count = 0
    replacements_made = []
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        updated_line = line
        
        # Check all patterns
        for pattern in IMAGE_PATTERNS:
            matches = list(re.finditer(pattern, line))
            for match in reversed(matches):  # Reverse to maintain positions
                original = match.group(0)
                
                # Extract the path (remove quotes)
                path = original.strip('"\'').strip()
                
                # Normalize path for lookup
                normalized = path.replace('\\', '/')
                if normalized.startswith('/uploads/'):
                    normalized = normalized[1:]
                if normalized.startswith('uploads/'):
                    normalized = normalized.replace('uploads/', '', 1)
                
                # Look up in mapping
                cloudinary_url = None
                for key in [normalized, f"uploads/{normalized}", f"/uploads/{normalized}", path]:
                    if key in mapping:
                        cloudinary_url = mapping[key]
                        break
                
                if cloudinary_url:
                    # Replace while preserving quotes
                    quote_char = original[0] if original[0] in ["'", '"'] else ''
                    if quote_char:
                        replacement = f"{quote_char}{cloudinary_url}{quote_char}"
                    else:
                        replacement = cloudinary_url
                    
                    updated_line = updated_line[:match.start()] + replacement + updated_line[match.end():]
                    replacement_count += 1
                    replacements_made.append((line_num, path, cloudinary_url))
        
        updated_lines.append(updated_line)
    
    if replacement_count > 0:
        print(f"  [UPDATE] {file_path.relative_to(FRONTEND_DIR)}: {replacement_count} replacement(s)")
        for line_num, old_path, new_url in replacements_made:
            print(f"    Line {line_num}: {old_path[:50]}... -> {new_url[:50]}...")
    
    return '\n'.join(updated_lines), replacement_count

def update_frontend_files():
    """Update all frontend files with Cloudinary URLs"""
    print("=" * 70)
    print("UPDATING FRONTEND IMAGE REFERENCES")
    print("=" * 70)
    print()
    
    # Load mapping
    mapping = load_mapping_file()
    if not mapping:
        print("[ERROR] No mappings found. Cannot continue.")
        return
    
    print(f"[INFO] Searching frontend files in: {FRONTEND_DIR}")
    print(f"[INFO] File extensions: {', '.join(FILE_EXTENSIONS)}")
    print()
    
    # Find all frontend files
    frontend_files = []
    for ext in FILE_EXTENSIONS:
        frontend_files.extend(FRONTEND_DIR.rglob(f"*{ext}"))
    
    # Filter out node_modules and dist folders
    frontend_files = [
        f for f in frontend_files
        if 'node_modules' not in str(f) and 'dist' not in str(f) and '.next' not in str(f)
    ]
    
    print(f"[INFO] Found {len(frontend_files)} frontend files to check")
    print()
    
    total_replacements = 0
    files_updated = 0
    
    # Process each file
    for file_path in sorted(frontend_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find references
            references = find_image_references(content, str(file_path))
            
            if references:
                # Replace paths
                updated_content, replacement_count = replace_image_paths(content, mapping, file_path)
                
                if replacement_count > 0:
                    # Write updated content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    total_replacements += replacement_count
                    files_updated += 1
        
        except Exception as e:
            print(f"  [ERROR] Failed to process {file_path.relative_to(FRONTEND_DIR)}: {e}")
            continue
    
    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"[OK] Files updated: {files_updated}")
    print(f"[OK] Total replacements: {total_replacements}")
    print()
    
    if files_updated > 0:
        print("[WARNING] IMPORTANT:")
        print("1. Review the changes using git diff")
        print("2. Test the application to ensure images load correctly")
        print("3. Commit the changes if everything works")
        print()

if __name__ == "__main__":
    update_frontend_files()

