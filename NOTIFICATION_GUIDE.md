# 🔔 Notification System Guide

## 📋 What You Already Have

### ✅ **Frontend (Complete)**
Your notification UI is **fully implemented** with:

1. **Notification Page** (`app/dashboard/notifications/page.tsx`)
   - Display all notifications
   - Mark as read/unread
   - Show timestamp and channel
   - Empty state when no notifications

2. **Notification Preferences** (`app/components/dashboard/NotificationPrefs.tsx`)
   - Toggle notification channels (Email, SMS, Push)
   - Toggle notification types (Deadline Reminders, New Matches, Status Updates)
   - Save preferences button
   - Beautiful UI with icons

### ✅ **Backend Structure (In Progress)**
Your notification backend has the framework:

1. **Service Layer** (`services/app/notifications/`)
   - ✅ Abstract base classes
   - ✅ Notification orchestrator
   - ⚠️ Email service (needs configuration)
   - ⚠️ SMS service (needs configuration)
   - ⚠️ Push service (needs configuration)

2. **Database Models**
   - ✅ NotificationPreference (user preferences)
   - ✅ NotificationHistory (delivery logs)
   - ✅ Notification (in-app notifications)

---

## 🎯 Notification Features You Can Use

### **1. In-App Notifications** ✅ (Already Working)
**What:** Notifications shown in the dashboard  
**Status:** Ready to use  
**No setup needed!**

**How to use:**
```typescript
// From frontend
const notifications = await getNotifications(userId, userEmail);
```

**Backend example:**
```python
# From Python backend
from app.notifications.service import send_notification

send_notification(
    db=db,
    user_id="user-123",
    title="New Scholarship Available!",
    body="Check out the AICTE scholarship that matches your profile",
    channel="in_app"
)
```

---

### **2. Email Notifications** ⚙️ (Needs Setup)

**What:** Send emails via SendGrid  
**Status:** Code ready, needs API key

#### **What You Need:**

1. **SendGrid Account** (Free tier available)
   - Sign up: https://sendgrid.com/free/
   - Free tier: 100 emails/day (enough for testing)

2. **API Key**
   - Get from: SendGrid Dashboard → Settings → API Keys
   - Create new key with "Full Access"

3. **Add to `.env` file:**
```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=EduPilot
```

#### **Features You Get:**

✅ **Welcome Email** - When user signs up  
✅ **Deadline Reminders** - 7 days and 2 days before deadline  
✅ **New Match Alerts** - When new opportunities match profile  
✅ **Status Updates** - When application status changes  
✅ **Custom Templates** - HTML email templates  

#### **Example Email Types:**

```python
# Deadline Reminder Email
{
    'subject': '⏰ Scholarship Deadline in 2 Days',
    'body': 'The AICTE scholarship deadline is approaching...',
    'html': '<html>...</html>'  # Optional HTML version
}

# New Match Email
{
    'subject': '🎓 New Scholarship Matches Your Profile',
    'body': 'We found 3 new scholarships that match your profile...'
}
```

---

### **3. SMS Notifications** ⚙️ (Needs Setup)

**What:** Send SMS via Twilio  
**Status:** Code ready, needs account

#### **What You Need:**

1. **Twilio Account** (Free trial available)
   - Sign up: https://www.twilio.com/try-twilio
   - Free trial: $15 credit (~450 SMS)
   - Get a phone number (free during trial)

2. **Credentials**
   - Account SID: From Twilio Console
   - Auth Token: From Twilio Console
   - Phone Number: From Twilio Phone Numbers

3. **Add to `.env` file:**
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

#### **Features You Get:**

✅ **Urgent Alerts** - Critical deadline reminders  
✅ **Verification Codes** - 2FA authentication  
✅ **Status Updates** - Short, important updates  
✅ **Opt-in/Opt-out** - Users control SMS preferences  

#### **SMS Examples:**

```
⏰ URGENT: AICTE scholarship deadline in 2 days. Apply now: https://...

✅ Your scholarship application was approved! Check your email for details.

🎓 3 new scholarships match your profile. View: https://...
```

#### **SMS Best Practices:**
- Keep under 160 characters
- Use only for urgent/important updates
- Respect user preferences (opt-out)
- Include opt-out info: "Reply STOP to unsubscribe"

---

### **4. Push Notifications** ⚙️ (Needs Setup)

**What:** Browser/Mobile push via Firebase Cloud Messaging (FCM)  
**Status:** Code ready, needs Firebase project

#### **What You Need:**

1. **Firebase Project** (Free)
   - Go to: https://console.firebase.google.com/
   - Create new project
   - Enable "Cloud Messaging"

2. **Get Credentials**
   - Project Settings → Cloud Messaging
   - Get Server Key
   - Get Sender ID

3. **Add to `.env` file:**
```bash
FCM_SERVER_KEY=AAAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FCM_SENDER_ID=123456789012
```

4. **Frontend Setup** (Add to your Next.js app):
```bash
npm install firebase
```

#### **Features You Get:**

✅ **Browser Notifications** - Desktop alerts  
✅ **Mobile Notifications** - iOS/Android apps  
✅ **Rich Notifications** - Images, actions, badges  
✅ **Offline Delivery** - Queued when user offline  
✅ **Click Actions** - Deep links to specific pages  

#### **Push Notification Example:**

```javascript
{
  title: "🎓 New Scholarship Match",
  body: "AICTE Research Grant matches your profile",
  icon: "/logo.png",
  badge: "/badge.png",
  data: {
    url: "/dashboard/scholarships/abc-123",
    opportunity_id: "abc-123"
  }
}
```

---

## 🎨 Notification Types Already Implemented

### **1. Deadline Reminders** ⏰
**When:** 7 days before and 2 days before deadline  
**Channels:** Email, SMS, Push, In-App  
**User Control:** Can toggle on/off in preferences

**Example:**
```
Title: "Scholarship Deadline Approaching"
Body: "The AICTE Scholarship deadline is in 2 days (Dec 15, 2024). 
       Complete your application now!"
```

### **2. New Matches** ✨
**When:** New opportunities match user profile  
**Channels:** Email, Push, In-App  
**User Control:** Can toggle on/off

**Example:**
```
Title: "3 New Opportunities Match Your Profile"
Body: "We found scholarships that match your engineering background 
       and financial needs. View them now!"
```

### **3. Status Updates** 📊
**When:** Application status changes  
**Channels:** Email, SMS, Push, In-App  
**User Control:** Can toggle on/off

**Example:**
```
Title: "Application Status Update"
Body: "Your AICTE scholarship application status changed to 'Under Review'"
```

---

## 🔧 Setup Instructions

### **Option 1: Test with In-App Only** (No setup needed) ✅

Everything works with in-app notifications:
```typescript
// Already working!
const notifications = await getNotifications(userId);
```

### **Option 2: Add Email (Recommended for testing)** 📧

1. **Sign up for SendGrid Free**
   - https://sendgrid.com/free/
   - Verify your email

2. **Get API Key**
   - Dashboard → Settings → API Keys → Create API Key
   - Copy the key (starts with `SG.`)

3. **Add to `.env`**
   ```bash
   SENDGRID_API_KEY=SG.your_key_here
   SENDGRID_FROM_EMAIL=noreply@yourdomain.com
   ```

4. **Test it**
   ```python
   from app.notifications.email import EmailNotificationService
   
   email_service = EmailNotificationService()
   result = await email_service.send(
       "user@example.com",
       {
           'subject': 'Test Email',
           'body': 'This is a test notification'
       }
   )
   print(result)  # {'success': True, 'message_id': '...'}
   ```

### **Option 3: Add SMS (For production)** 📱

1. **Sign up for Twilio**
   - https://www.twilio.com/try-twilio
   - Get free trial credit

2. **Get Phone Number**
   - Console → Phone Numbers → Buy a number
   - Free during trial

3. **Add to `.env`**
   ```bash
   TWILIO_ACCOUNT_SID=ACxxxxxxxx
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### **Option 4: Add Push (For mobile/PWA)** 🔔

1. **Create Firebase Project**
   - https://console.firebase.google.com/
   - Add web app to project

2. **Get Config**
   - Project Settings → General → Web Apps
   - Copy config

3. **Add to frontend**
   ```javascript
   // firebase-config.js
   const firebaseConfig = {
     apiKey: "...",
     authDomain: "...",
     projectId: "...",
     messagingSenderId: "..."
   };
   ```

---

## 📊 User Notification Preferences

Your users can control notifications via the UI:

### **Channels:**
- ✉️ **Email** - Receive updates via email
- 📱 **SMS** - Get urgent alerts via text
- 🔔 **Push** - Browser/app notifications

### **Types:**
- ⏰ **Deadline Reminders** - 7-day and 2-day alerts
- ✨ **New Matches** - When opportunities match profile
- 📊 **Status Updates** - Application status changes

**All preferences are saved per user in the database!**

---

## 🎯 Quick Test (No Setup Required)

### **1. Test In-App Notifications:**

```bash
# In services directory
cd d:\student\student-ai-copilot\services
python

# In Python shell
from app.db.session import SessionLocal
from app.notifications.service import send_notification

db = SessionLocal()
send_notification(
    db=db,
    user_id="test-user-123",
    title="Test Notification",
    body="This is a test notification!",
    channel="in_app"
)
db.close()

# Now check in the UI at /dashboard/notifications
```

### **2. Test Orchestrator (Multi-channel):**

```python
from app.notifications.orchestrator import NotificationOrchestrator
from app.notifications.service import NotificationType
from app.db.session import SessionLocal

db = SessionLocal()
orchestrator = NotificationOrchestrator(db)

# This will send to all enabled channels based on user preferences
result = await orchestrator.send_notification(
    user_id="test-user-123",
    notification_type=NotificationType.NEW_MATCH,
    title="New Scholarship Available",
    body="A new scholarship matches your profile!"
)

print(result)
db.close()
```

---

## 📝 Summary

### **What Works Now (No Setup):** ✅
- ✅ In-app notifications
- ✅ User preferences UI
- ✅ Notification history
- ✅ Mark as read/unread
- ✅ Notification preferences save/load

### **What Needs Setup:** ⚙️
- ⚙️ Email (SendGrid API key)
- ⚙️ SMS (Twilio credentials)
- ⚙️ Push (Firebase project)

### **Recommended Next Steps:**

1. **Start with In-App** - Already works, test it!
2. **Add Email** - Free tier, easy to set up
3. **Add SMS** (optional) - For urgent alerts only
4. **Add Push** (optional) - For mobile experience

---

## 🔗 Useful Links

- **SendGrid:** https://sendgrid.com/free/
- **Twilio:** https://www.twilio.com/try-twilio
- **Firebase:** https://console.firebase.google.com/
- **Your Notification UI:** http://localhost:3001/dashboard/notifications

---

**You have a fully functional notification system!** Start with in-app notifications (already working), then add external channels as needed. 🎉
