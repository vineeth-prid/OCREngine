# 🔐 OCR ENGINE - ACCESS DETAILS & LOGIN INFORMATION

## 🌐 Application URLs

### Frontend Application
**URL:** http://localhost:3000
- User registration and login
- Dashboard
- Form schema builder
- Document upload
- Document processing

### Backend API
**URL:** http://localhost:8001
**API Documentation:** http://localhost:8001/docs
**Health Check:** http://localhost:8001/api/health

---

## 👤 TEST ACCOUNTS

### Pre-Created Admin Account
**Email:** `admin@ocrengine.com`
**Password:** `SecurePass123!`
**Organization:** OCR Engine Demo
**Role:** Admin (full access)

### New Test Account (Just Created)
**Email:** `admin@demo.com`
**Password:** `Admin123!`
**Organization:** Demo Organization
**Role:** Admin (full access)

---

## 📋 HOW TO ACCESS

### 1. Register New Account (Recommended)
1. Go to: http://localhost:3000
2. Click "Sign up" or go to http://localhost:3000/register
3. Fill in:
   - **Full Name:** Your name
   - **Organization Name:** Your company name (required)
   - **Email:** your@email.com
   - **Password:** Minimum 8 characters
4. Click "Create Account"
5. You'll be automatically logged in and assigned Admin role

### 2. Login with Existing Account
1. Go to: http://localhost:3000/login
2. Enter email and password
3. Click "Sign In"

---

## 🎯 NAVIGATION

After login, you can access:

### Dashboard
**URL:** http://localhost:3000/dashboard
- View usage statistics
- See total documents and schemas
- Quick actions

### Form Schemas
**URL:** http://localhost:3000/schemas
- Create custom document schemas
- Define fields and validation rules
- Manage existing schemas

### Documents
**URL:** http://localhost:3000/documents
- Upload documents (PDF, JPG, PNG)
- Select form schema
- View processing status
- See extraction results

### Admin Panel
**URL:** http://localhost:3000/admin
- System statistics
- Configuration management
- Tenant overview
- Document status monitoring

---

## 🔑 USER ROLES & PERMISSIONS

### Admin Role (Auto-assigned to first user)
✅ Full system access
✅ Create/edit/delete schemas
✅ Upload and process documents
✅ Manage users
✅ View admin panel
✅ Configure system settings

### Manager Role
✅ Create/edit schemas
✅ Upload and process documents
✅ View documents
❌ No admin panel access

### Reviewer Role
✅ View documents
✅ Review and approve extractions
❌ Cannot upload documents
❌ No admin panel access

### Viewer Role
✅ View documents only
❌ No editing or uploading
❌ No admin panel access

---

## 🚀 QUICK START GUIDE

### Step 1: Register & Login
1. Go to http://localhost:3000
2. Register new account with organization name
3. First user becomes Admin automatically

### Step 2: Create Form Schema
1. Navigate to "Form Schemas"
2. Click "Create Schema"
3. Enter schema name (e.g., "Invoice")
4. Add description
5. Click "Create"
6. (Optional) Add custom fields later

### Step 3: Upload Document
1. Navigate to "Documents"
2. Click "Select Document"
3. Choose PDF/JPG/PNG file
4. (Optional) Select form schema
5. Click "Upload & Process"
6. Document will be queued for OCR processing

### Step 4: View Results
1. Document status changes: uploaded → processing → completed
2. View confidence scores
3. See extracted data (if schema was selected)
4. Review and approve

### Step 5: Admin Panel
1. Navigate to "Admin"
2. View system statistics
3. Monitor all tenants
4. Check document processing stats
5. Manage configurations

---

## 🔧 API ACCESS (For Developers)

### Get API Token
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "your_password"
  }'
```

### Use Token in Requests
```bash
TOKEN="your_token_here"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/auth/me
```

### API Documentation
Interactive API docs: http://localhost:8001/docs
- Test all endpoints
- See request/response schemas
- Try authentication

---

## 📊 DEFAULT SUBSCRIPTION

All new accounts get:
- **Tier:** Free
- **Monthly Limit:** 100 pages
- **OCR Engines:** Tesseract + RapidOCR
- **LLM Processing:** Mock (configurable)
- **Support:** Community

---

## 🛠️ TROUBLESHOOTING

### Cannot Login
- Check email/password
- Ensure account is created
- Try registering again with different email

### Registration Failed
- Check all required fields are filled
- Organization name is mandatory
- Password must be 8+ characters
- Email must be valid format

### Page Not Loading
- Check backend is running: `supervisorctl status backend`
- Check frontend is running: `supervisorctl status frontend`
- Restart services: `supervisorctl restart all`

### Document Upload Failed
- Check file type (PDF, JPG, PNG only)
- File size should be reasonable
- Check backend logs: `tail -f /var/log/supervisor/backend.out.log`

---

## 📞 SUPPORT

### Check Service Status
```bash
supervisorctl status
```

### View Backend Logs
```bash
tail -f /var/log/supervisor/backend.out.log
```

### View Frontend Logs
```bash
tail -f /var/log/supervisor/frontend.out.log
```

### Restart Services
```bash
# Restart all
supervisorctl restart all

# Restart specific service
supervisorctl restart backend
supervisorctl restart frontend
```

---

## ✅ QUICK TEST

1. **Register:** http://localhost:3000/register
   - Organization: Test Company
   - Email: test@example.com
   - Password: TestPass123!

2. **Login:** Use credentials from step 1

3. **Create Schema:** Name it "Test Schema"

4. **Upload Document:** Any PDF or image

5. **View Admin:** Check system stats

---

## 🎉 READY TO USE!

The platform is fully configured and ready. Your first registered user will automatically become the Admin of your organization.

**Main URL:** http://localhost:3000

**Enjoy your OCR Engine platform!** 🚀
