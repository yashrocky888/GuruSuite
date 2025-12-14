#!/bin/bash
# Install gcloud CLI

echo "📦 Installing Google Cloud SDK..."

# Download and install
curl https://sdk.cloud.google.com | bash

# Add to PATH
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Initialize
exec -l $SHELL
source "$HOME/google-cloud-sdk/path.bash.inc"

echo "✅ gcloud installed!"
gcloud --version | head -1
