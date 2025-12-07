#!/bin/bash
echo "=================================="
echo "FINAL COMPREHENSIVE TEST"
echo "=================================="
echo ""

# Test 1: Backend Health
echo "1. Testing Backend Health..."
HEALTH=$(curl -s http://localhost:8001/api/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Backend is healthy"
else
    echo "   ❌ Backend health check failed"
    exit 1
fi

# Test 2: Registration
echo "2. Testing Registration..."
REG=$(curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test'$(date +%s)'@test.com","password":"Test123!","full_name":"Test","organization_name":"Test Org"}')
if echo "$REG" | grep -q "access_token"; then
    echo "   ✅ Registration works"
else
    echo "   ❌ Registration failed"
    exit 1
fi

# Test 3: Login
echo "3. Testing Login..."
LOGIN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ocrengine.com","password":"SecurePass123!"}')
if echo "$LOGIN" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "   ✅ Login works"
else
    echo "   ❌ Login failed"
    exit 1
fi

# Test 4: Form Creation
echo "4. Testing Form Creation..."
FORM=$(curl -s -X POST http://localhost:8001/api/schemas/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Test Form","description":"Test","fields":[{"field_name":"test","field_label":"Test","field_type":"text","is_required":false,"display_order":0}]}')
if echo "$FORM" | grep -q '"id"'; then
    echo "   ✅ Form creation works"
else
    echo "   ❌ Form creation failed"
    exit 1
fi

# Test 5: List Forms
echo "5. Testing Form Listing..."
FORMS=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/schemas/)
if echo "$FORMS" | grep -q "Test Form"; then
    echo "   ✅ Form listing works"
else
    echo "   ❌ Form listing failed"
    exit 1
fi

# Test 6: Services Status
echo "6. Checking Services..."
if supervisorctl status backend | grep -q "RUNNING"; then
    echo "   ✅ Backend service running"
else
    echo "   ❌ Backend not running"
    exit 1
fi

if supervisorctl status frontend | grep -q "RUNNING"; then
    echo "   ✅ Frontend service running"
else
    echo "   ❌ Frontend not running"
    exit 1
fi

if supervisorctl status celery_worker | grep -q "RUNNING"; then
    echo "   ✅ Celery worker running"
else
    echo "   ❌ Celery not running"
    exit 1
fi

# Test 7: Database
echo "7. Checking Database..."
if [ -f /app/backend/ocrengine.db ]; then
    echo "   ✅ Database file exists"
else
    echo "   ❌ Database file missing"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ ALL TESTS PASSED!"
echo "=================================="
echo ""
echo "Platform is fully operational!"
echo ""
echo "Login with:"
echo "  Email: admin@ocrengine.com"
echo "  Password: SecurePass123!"
echo ""
echo "Documentation: /app/PRODUCTION_READY.md"
