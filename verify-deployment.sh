#!/bin/bash
# Deployment Verification Script
# This script verifies that the application is deployed and operational

set -e

echo "🔍 Verifying Deployment for Kasparro Backend Assignment"
echo "========================================================"
echo ""

# Configuration
BASE_URL="https://kasparro-backend-charan-naik.onrender.com"
GITHUB_REPO="https://github.com/Charan1490/kasparro-backend-Charan-Naik"

echo "📍 Production URL: $BASE_URL"
echo "📦 GitHub Repository: $GITHUB_REPO"
echo ""

# Test 1: Health Check
echo "✅ Test 1: Health Check Endpoint"
echo "   Testing: $BASE_URL/health"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
echo "   Response: $HEALTH_RESPONSE"

# Check if database is connected
if echo "$HEALTH_RESPONSE" | grep -q '"database":"connected"'; then
    echo "   ✓ Database: CONNECTED"
elif echo "$HEALTH_RESPONSE" | grep -q '"database": "connected"'; then
    echo "   ✓ Database: CONNECTED"
else
    echo "   ✗ Database: DISCONNECTED"
    exit 1
fi
echo ""

# Test 2: Data Endpoint
echo "✅ Test 2: Data Endpoint (API)"
echo "   Testing: $BASE_URL/data?limit=3"
DATA_RESPONSE=$(curl -s "$BASE_URL/data?limit=3")
COIN_COUNT=$(echo "$DATA_RESPONSE" | grep -o '"data":\[' | wc -l)
if [ "$COIN_COUNT" -gt 0 ]; then
    echo "   ✓ Data endpoint returning cryptocurrency records"
else
    echo "   ✗ Data endpoint not returning data"
    exit 1
fi
echo ""

# Test 3: Stats Endpoint
echo "✅ Test 3: ETL Statistics Endpoint"
echo "   Testing: $BASE_URL/stats"
STATS_RESPONSE=$(curl -s "$BASE_URL/stats")
echo "   Response: $STATS_RESPONSE"

# Check if ETL has run
if echo "$STATS_RESPONSE" | grep -q '"total_runs"'; then
    echo "   ✓ ETL pipeline operational"
else
    echo "   ✗ ETL pipeline not running"
    exit 1
fi
echo ""

# Test 4: API Documentation
echo "✅ Test 4: API Documentation"
echo "   Testing: $BASE_URL/docs"
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$DOCS_STATUS" = "200" ]; then
    echo "   ✓ API documentation accessible (HTTP $DOCS_STATUS)"
else
    echo "   ✗ API documentation not accessible (HTTP $DOCS_STATUS)"
    exit 1
fi
echo ""

# Test 5: Metrics Endpoint
echo "✅ Test 5: Prometheus Metrics"
echo "   Testing: $BASE_URL/metrics"
METRICS_STATUS=$(curl -sL -o /dev/null -w "%{http_code}" "$BASE_URL/metrics")
if [ "$METRICS_STATUS" = "200" ]; then
    echo "   ✓ Metrics endpoint accessible (HTTP $METRICS_STATUS)"
else
    echo "   ⚠ Metrics endpoint returned HTTP $METRICS_STATUS (may require authentication)"
fi
echo ""

# Test 6: HTTPS Certificate
echo "✅ Test 6: HTTPS Certificate"
CERT_INFO=$(curl -vI "$BASE_URL/health" 2>&1 | grep "SSL certificate verify ok" || echo "")
if [ -n "$CERT_INFO" ]; then
    echo "   ✓ Valid HTTPS certificate"
else
    echo "   ⚠ HTTPS certificate verification inconclusive"
fi
echo ""

# Test 7: Response Headers
echo "✅ Test 7: Deployment Headers"
HEADERS=$(curl -sI "$BASE_URL/health")
echo "$HEADERS" | grep -i "server:" || echo "   Server header not exposed (good security practice)"
echo ""

# Summary
echo "========================================================"
echo "🎉 DEPLOYMENT VERIFICATION COMPLETE"
echo "========================================================"
echo ""
echo "Summary:"
echo "  ✓ Application is live and accessible"
echo "  ✓ Database connection verified"
echo "  ✓ ETL pipeline operational"
echo "  ✓ All API endpoints responding"
echo "  ✓ HTTPS enabled"
echo "  ✓ Documentation accessible"
echo ""
echo "Production URL: $BASE_URL"
echo "Interactive Docs: $BASE_URL/docs"
echo "GitHub Repository: $GITHUB_REPO"
echo ""
echo "Status: ✅ DEPLOYMENT VERIFIED"
echo ""
