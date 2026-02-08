#!/bin/bash
# ENV DEPLOY LOCK: Fail if OPENAI_API_KEY missing after deploy.
set -e
REGION="${REGION:-asia-south1}"
SERVICE="${SERVICE:-guru-api}"
echo "Verifying $SERVICE in $REGION..."
REV=$(gcloud run services describe $SERVICE --region $REGION --format="value(status.latestReadyRevisionName)" 2>/dev/null)
echo "Latest revision: $REV"
ENV=$(gcloud run services describe $SERVICE --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || true)
if echo "$ENV" | grep -q "OPENAI_API_KEY"; then
    echo "OK: OPENAI_API_KEY present"
else
    echo "FAIL: OPENAI_API_KEY missing. Run: gcloud run services update $SERVICE --region $REGION --set-env-vars OPENAI_API_KEY=..."
    exit 1
fi
