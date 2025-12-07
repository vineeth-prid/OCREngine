#!/bin/bash

echo "=================================="
echo "OCR ENGINE - REGISTRATION TEST"
echo "=================================="
echo ""

# Generate unique credentials
TIMESTAMP=$(date +%s)
TEST_EMAIL="test${TIMESTAMP}@example.com"
TEST_PASSWORD="TestPass123!"
TEST_NAME="Test User ${TIMESTAMP}"
TEST_ORG="Test Organization ${TIMESTAMP}"

echo "Test Credentials:"
echo "  Email: ${TEST_EMAIL}"
echo "  Password: ${TEST_PASSWORD}"
echo "  Name: ${TEST_NAME}"
echo "  Organization: ${TEST_ORG}"
echo ""

echo "=================================="
echo "Step 1: Testing Backend Health"
echo "=================================="
HEALTH=$(curl -s http://localhost:8001/api/health)
echo "$HEALTH" | python -m json.tool
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi
echo ""

echo "=================================="
echo "Step 2: Testing Registration API"
echo "=================================="
REG_RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"full_name\": \"${TEST_NAME}\",
    \"organization_name\": \"${TEST_ORG}\"
  }")

echo "$REG_RESPONSE" | python -m json.tool

if echo "$REG_RESPONSE" | grep -q "access_token"; then
    echo "✅ Registration successful!"
    TOKEN=$(echo "$REG_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "Token: ${TOKEN:0:50}..."
else
    echo "❌ Registration failed"
    exit 1
fi
echo ""

echo "=================================="
echo "Step 3: Testing Login API"
echo "=================================="
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\"
  }")

echo "$LOGIN_RESPONSE" | python -m json.tool

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ Login successful!"
    LOGIN_TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
else
    echo "❌ Login failed"
    exit 1
fi
echo ""

echo "=================================="
echo "Step 4: Testing Authenticated Endpoint"
echo "=================================="
ME_RESPONSE=$(curl -s -X GET http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer ${LOGIN_TOKEN}")

echo "$ME_RESPONSE" | python -m json.tool

if echo "$ME_RESPONSE" | grep -q "email"; then
    echo "✅ Authenticated endpoint working!"
else
    echo "❌ Authenticated endpoint failed"
    exit 1
fi
echo ""

echo "=================================="
echo "Step 5: Testing Tenant Info"
echo "=================================="
TENANT_RESPONSE=$(curl -s -X GET http://localhost:8001/api/tenants/me \
  -H "Authorization: Bearer ${LOGIN_TOKEN}")

echo "$TENANT_RESPONSE" | python -m json.tool

if echo "$TENANT_RESPONSE" | grep -q "slug"; then
    echo "✅ Tenant info retrieved!"
else
    echo "❌ Tenant info failed"
    exit 1
fi
echo ""

echo "=================================="
echo "Step 6: Testing Usage Stats"
echo "=================================="
USAGE_RESPONSE=$(curl -s -X GET http://localhost:8001/api/tenants/me/usage \
  -H "Authorization: Bearer ${LOGIN_TOKEN}")

echo "$USAGE_RESPONSE" | python -m json.tool

if echo "$USAGE_RESPONSE" | grep -q "max_pages_per_month"; then
    echo "✅ Usage stats retrieved!"
else
    echo "❌ Usage stats failed"
    exit 1
fi
echo ""

echo "=================================="
echo "Step 7: Checking Services"
echo "=================================="
echo "Backend status:"
supervisorctl status backend | grep RUNNING && echo "✅ Backend running" || echo "❌ Backend not running"
echo ""
echo "Frontend status:"
supervisorctl status frontend | grep RUNNING && echo "✅ Frontend running" || echo "❌ Frontend not running"
echo ""

echo "=================================="
echo "✅ ALL TESTS PASSED!"
echo "=================================="
echo ""
echo "You can now login with:"
echo "  Email: ${TEST_EMAIL}"
echo "  Password: ${TEST_PASSWORD}"
echo ""
echo "Or use pre-created accounts:"
echo "  Email: admin@ocrengine.com"
echo "  Password: SecurePass123!"
echo ""
echo "  Email: admin@demo.com"
echo "  Password: Admin123!"
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8001/docs"
echo "=================================="
