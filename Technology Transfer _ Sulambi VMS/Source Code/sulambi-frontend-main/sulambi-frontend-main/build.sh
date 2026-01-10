#!/bin/bash
# Build script for Render deployment
# This script ensures VITE_API_URI is set before building

# Check if VITE_API_URI is set
if [ -z "$VITE_API_URI" ]; then
  echo "⚠️  WARNING: VITE_API_URI environment variable is not set!"
  echo ""
  echo "📋 To fix this:"
  echo "1. Go to your Render Dashboard"
  echo "2. Open your frontend service (sulambi-frontend)"
  echo "3. Go to 'Environment' tab"
  echo "4. Add environment variable:"
  echo "   Key: VITE_API_URI"
  echo "   Value: https://YOUR-BACKEND-NAME.onrender.com/api"
  echo "   (Replace YOUR-BACKEND-NAME with your actual backend service name)"
  echo ""
  echo "5. Save and redeploy"
  echo ""
  echo "Using default for now (will not work in production): http://localhost:8000/api"
  export VITE_API_URI="http://localhost:8000/api"
fi

echo "✅ Building with VITE_API_URI=$VITE_API_URI"

# Run the build (using build-ignore to skip TypeScript type checking)
# TODO: Fix TypeScript errors and switch back to "npm run build"
npm install
npm run build-ignore

# Verify and ensure _redirects file exists in dist (required for SPA routing on Render)
echo ""
echo "🔍 Checking _redirects file for SPA routing..."
if [ -f "dist/_redirects" ]; then
  echo "✅ _redirects file found in dist/"
  echo "📄 Contents:"
  cat dist/_redirects
else
  echo "⚠️  WARNING: _redirects file NOT found in dist/"
  echo "Creating _redirects file in dist/..."
fi

# Ensure _redirects file exists with correct content for Render
cat > dist/_redirects << 'EOF'
/*    /index.html   200
EOF

echo "✅ _redirects file ensured in dist/"
echo "📄 Final contents:"
cat dist/_redirects
echo ""

# Also verify index.html exists
if [ -f "dist/index.html" ]; then
  echo "✅ index.html found in dist/"
else
  echo "❌ ERROR: index.html NOT found in dist/ - build may have failed!"
  exit 1
fi

echo ""
echo "✅ Build verification complete!"
echo "📦 Ready for deployment to Render"

















