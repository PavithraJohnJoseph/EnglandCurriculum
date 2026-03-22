# Gmail Email Setup Guide for Production
==========================================

## Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com
2. Click "Security" in the left menu
3. Under "Signing in to Google", click "2-Step Verification"
4. Follow the steps to enable 2FA

## Step 2: Generate App Password
1. In the same "Security" section, find "App passwords"
2. You might need to sign in again
3. Select "Mail" from the first dropdown
4. Select "Windows Computer" from the second dropdown
5. Click "Generate"
6. Copy the 16-character password that appears

## Step 3: Update .env.production
Edit your .env.production file and update these lines:

```
EMAIL_HOST_USER=your-gmail-address@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=your-gmail-address@gmail.com
```

## Step 4: Test Email (Optional)
After deployment, you can test email by:
1. Creating a user account
2. The system will send welcome emails automatically

## Troubleshooting
- If emails don't send, check your Gmail spam folder
- Make sure "Less secure app access" is OFF (2FA + App Passwords is the secure way)
- App Passwords are specific to each app/device

## Alternative: SendGrid (More Professional)
If you prefer a more professional email service:

1. Sign up at https://sendgrid.com
2. Create an API key
3. Update .env.production:
```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```