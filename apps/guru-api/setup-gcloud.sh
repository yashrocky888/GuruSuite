#!/bin/bash
# Setup gcloud with correct Python path

export CLOUDSDK_PYTHON=$(which python3)
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"

echo "✅ gcloud configured"
echo "Python: $CLOUDSDK_PYTHON"
echo ""

# Check if gcloud works
if gcloud --version &>/dev/null; then
    echo "✅ gcloud is ready!"
    echo ""
    echo "Next steps:"
    echo "1. Authenticate: gcloud auth login"
    echo "2. Set project: gcloud config set project YOUR_PROJECT_ID"
    echo "3. Deploy: ./deploy-firebase.sh"
else
    echo "❌ gcloud not working. Try: gcloud components reinstall"
fi
