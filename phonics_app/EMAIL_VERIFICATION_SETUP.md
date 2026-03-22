# 📧 Email Verification Setup Guide

## Current Status

Your email verification logic **is working correctly**. The issue is that emails are currently being sent to the **terminal console** instead of actual email addresses.

## Quick Fix: See Emails in Your Terminal

**Right now**, when a user signs up, the verification email is printed to the terminal where your Django server is running.

### To see the emails:

1. Look at the terminal where you ran `python manage.py runserver`
2. After signing up, scroll up to find the email content
3. Copy the verification link from the terminal
4. Paste it in your browser to verify

The email will look something like:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Verify Your Email - Year 1 Phonics
From: noreply@phonicsapp.com
To: pavithra.ds@gmail.com

Hi there,

Thanks for signing up! Please verify your email by clicking:
http://localhost:8000/verify-email/MQ/abc123-token/

This link expires in 24 hours.
```

---

## Send Real Emails (Gmail Configuration)

To send actual emails to users' inboxes:

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** (left sidebar)
3. Under "How you sign in to Google", enable **2-Step Verification** (if not already enabled)
4. Go back to Security, scroll down to "2-Step Verification"
5. At the bottom, click **App passwords**
6. Select app: **Mail**
7. Select device: **Other (Custom name)** → Type "Phonics App"
8. Click **Generate**
9. Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)

### Step 2: Update Your .env File

Open `phonics_app/.env` and update these lines:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important:** 
- Remove any spaces from the App Password
- Use your **App Password**, NOT your regular Gmail password
- The DEFAULT_FROM_EMAIL should be the same as EMAIL_HOST_USER

### Step 3: Restart Your Django Server

```bash
# Stop the server (Ctrl+C)
# Then restart:
python manage.py runserver
```

---

## Testing Email Delivery

After configuration, test email sending:

1. Sign up with a new user
2. Check the actual email inbox
3. Click the verification link

### Troubleshooting

- **Emails in spam?** Check your spam/junk folder
- **App Password not working?** Make sure 2-Step Verification is enabled
- **Still not sending?** Check terminal for error messages
- **Gmail blocking sign-in?** Allow less secure app access: https://myaccount.google.com/lesssecureapps

---

## What Changed

✅ Updated `settings.py` to automatically use SMTP when email credentials are provided  
✅ Updated `.env` file with email configuration placeholders  
✅ Email verification is fully implemented and working  
✅ Emails show in console until you configure Gmail credentials  

