# 🔧 TROUBLESHOOTING GUIDE - OCR ENGINE

## ✅ VERIFICATION STATUS

**Backend:** ✅ Fully tested and working
**Frontend:** ✅ Compiled successfully
**Registration API:** ✅ Tested and working
**Login API:** ✅ Tested and working
**Database:** ✅ PostgreSQL operational
**Services:** ✅ All running

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue 1: "Registration Failed" Error

#### Possible Causes:
1. **Network/CORS Issue** - Frontend can't reach backend
2. **Duplicate Email** - Email already registered
3. **Invalid Password** - Password < 8 characters
4. **Browser Cache** - Old code cached

#### Solutions:

**A. Check Browser Console (MOST IMPORTANT)**
1. Open browser (Chrome/Firefox)
2. Press F12 to open Developer Tools
3. Go to "Console" tab
4. Try registration again
5. Look for red error messages
6. Share the error message

**B. Clear Browser Cache**
```
1. Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh page (Ctrl+F5 or Cmd+Shift+R)
```

**C. Use Different Email**
- Try with: `user$(date +%s)@test.com`
- Or any email you haven't used before

**D. Check Password Requirements**
- Minimum 8 characters
- Must include letters and numbers
- Try: `TestPass123!`

**E. Test Backend Directly**
Open terminal and run:
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "direct_test@example.com",
    "password": "TestPass123!",
    "full_name": "Direct Test",
    "organization_name": "Test Org"
  }'
```

If this works, issue is in frontend/browser.

---

### Issue 2: Page Won't Load

#### Solutions:

**A. Check Services**
```bash
supervisorctl status
```

Expected output:
```
backend    RUNNING
frontend   RUNNING
```

**B. Restart Services**
```bash
supervisorctl restart all
sleep 15
supervisorctl status
```

**C. Check Logs**
```bash
# Backend logs
tail -50 /var/log/supervisor/backend.out.log

# Frontend logs
tail -50 /var/log/supervisor/frontend.out.log
```

---

### Issue 3: "Cannot Connect" or Network Error

#### Solutions:

**A. Verify Backend URL**
In browser console, check:
```javascript
console.log(process.env.REACT_APP_BACKEND_URL)
```

**B. Test Backend Health**
```bash
curl http://localhost:8001/api/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "OCR Engine API",
  "version": "1.0.0"
}
```

**C. Check CORS**
The backend now allows all origins. CORS should not be an issue.

---

### Issue 4: Login Works but Registration Doesn't

#### This means:
- Backend is working
- Network is fine
- Specific registration issue

#### Solutions:

**A. Check for Duplicate Email**
Try with a completely new email:
```
newemail$(date +%s)@test.com
```

**B. Check Browser Network Tab**
1. Open Developer Tools (F12)
2. Go to "Network" tab
3. Try registration
4. Look for `/api/auth/register` request
5. Click on it
6. Check "Response" tab
7. Share the error message

---

### Issue 5: After Registration, Still Seeing Login Page

#### Solutions:

**A. Check localStorage**
In browser console:
```javascript
console.log(localStorage.getItem('token'))
console.log(localStorage.getItem('user'))
```

**B. Clear and Try Again**
```javascript
localStorage.clear()
location.reload()
```

---

## 🔍 DIAGNOSTIC COMMANDS

### Run Full Test Suite
```bash
/app/test_registration_flow.sh
```

This tests:
- ✅ Backend health
- ✅ Registration API
- ✅ Login API
- ✅ Authenticated endpoints
- ✅ Tenant info
- ✅ Usage stats
- ✅ Service status

### Check Database
```bash
sudo -u postgres psql -d ocrengine -c "SELECT id, email, tenant_id FROM users ORDER BY id DESC LIMIT 5;"
```

### Check Tenants
```bash
sudo -u postgres psql -d ocrengine -c "SELECT id, name, slug FROM tenants ORDER BY id DESC LIMIT 5;"
```

### View Recent Backend Logs
```bash
tail -100 /var/log/supervisor/backend.out.log | grep -E "POST /api/auth|ERROR|error"
```

### Check Frontend Compilation
```bash
tail -50 /var/log/supervisor/frontend.out.log | grep -E "Compiled|Failed|error"
```

---

## 🎯 WORKING TEST ACCOUNTS

These accounts are already created and verified:

### Account 1: Original Admin
```
Email: admin@ocrengine.com
Password: SecurePass123!
Organization: OCR Engine Demo
```

### Account 2: Demo Admin
```
Email: admin@demo.com
Password: Admin123!
Organization: Demo Organization
```

### Account 3: Latest Test
```
Email: test1765100280@example.com
Password: TestPass123!
Organization: Test Organization 1765100280
```

**Try logging in with any of these first to verify system is working!**

---

## 🌐 ACCESS URLS

### Development (localhost)
- Frontend: http://localhost:3000
- Backend: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Check Your Current URL
If you're seeing a different domain (like preview.emergentagent.com), that's fine. The app should work with dynamic URLs.

---

## 📊 STEP-BY-STEP REGISTRATION TEST

1. **Open Frontend**
   - Go to http://localhost:3000

2. **Open Browser Console**
   - Press F12
   - Click "Console" tab
   - Leave it open

3. **Click "Sign up"**
   - Or go to /register

4. **Fill Form**
   - Full Name: Test User
   - Organization: Test Company 2025
   - Email: test123@example.com
   - Password: TestPass123!

5. **Click "Create Account"**
   - Watch console for errors
   - Should redirect to dashboard

6. **If Error Appears**
   - Read error message in console
   - Take screenshot
   - Share with developer

---

## 🚨 EMERGENCY FIXES

### Complete Reset
```bash
# Stop services
supervisorctl stop all

# Restart PostgreSQL
service postgresql restart

# Start services
supervisorctl start all

# Wait for startup
sleep 20

# Check status
supervisorctl status
```

### Re-run Test Suite
```bash
/app/test_registration_flow.sh
```

### Check All Services
```bash
service postgresql status
service redis-server status
supervisorctl status
```

---

## 📞 WHAT TO SHARE IF ISSUE PERSISTS

1. **Browser Console Screenshot**
   - F12 → Console tab → Screenshot of error

2. **Network Tab Info**
   - F12 → Network tab → Find /api/auth/register
   - Screenshot of request/response

3. **Test Results**
   ```bash
   /app/test_registration_flow.sh
   ```

4. **Backend Logs**
   ```bash
   tail -50 /var/log/supervisor/backend.err.log
   ```

5. **Service Status**
   ```bash
   supervisorctl status
   ```

---

## ✅ CONFIRMED WORKING

As of last test:
- ✅ Backend API: Fully functional
- ✅ Registration: Creates user + tenant + subscription
- ✅ Login: Returns JWT token
- ✅ Authentication: Token validation working
- ✅ Multi-tenancy: Tenant isolation working
- ✅ Database: All tables operational
- ✅ Frontend: Compiled and accessible

**The system is working. If you're experiencing issues, it's likely:**
1. Browser cache (clear it)
2. Duplicate email (try new email)
3. Network issue (check console)

---

## 🎉 QUICK VERIFICATION

**Test login with existing account:**
1. Go to http://localhost:3000/login
2. Email: `admin@ocrengine.com`
3. Password: `SecurePass123!`
4. Click "Sign In"

**If this works → System is operational!**
**If this fails → Run diagnostic commands above**
