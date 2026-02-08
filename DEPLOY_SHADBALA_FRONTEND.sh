#!/bin/bash
# Shadbala Frontend Deployment Script (Vercel)
# Run this script to deploy Shadbala UI

set -e

echo "🚀 SHADBALA FRONTEND DEPLOYMENT"
echo "==============================="
echo ""

cd "$(dirname "$0")/apps/guru-web/guru-web"

# Verify build exists
if [ ! -d ".next" ]; then
    echo "📦 Building frontend..."
    npm run build
fi

echo "✅ Build verified"
echo ""
echo "🔄 Step 2: Deploying to Vercel..."
echo ""

# Deploy to Vercel
vercel --prod

echo ""
echo "✅ Frontend deployment complete!"
echo ""
echo "🌐 Frontend URL: (Check Vercel dashboard for URL)"
echo "   Shadbala page: <your-vercel-url>/shadbala"
echo ""
