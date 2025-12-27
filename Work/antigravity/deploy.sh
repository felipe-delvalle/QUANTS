#!/bin/bash
# Deployment script for Antigravity to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}No project ID set. Please set it:${NC}"
    echo "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}Deploying Antigravity to Google Cloud Run${NC}"
echo -e "Project ID: ${YELLOW}$PROJECT_ID${NC}"
echo ""

# Ask for confirmation
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

# Set region
REGION=${REGION:-us-central1}
echo -e "${GREEN}Using region: $REGION${NC}"

# Build and deploy using Cloud Build
echo -e "${GREEN}Starting Cloud Build...${NC}"
gcloud builds submit --config=cloudbuild.yaml

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo "Service URL:"
gcloud run services describe antigravity --region=$REGION --format='value(status.url)'
echo ""
echo "Test the service:"
echo "curl \$(gcloud run services describe antigravity --region=$REGION --format='value(status.url)')"

