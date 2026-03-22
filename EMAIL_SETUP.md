# Email Configuration Guide for Password Reset

## Development Setup (Current)

In **development** (`DEBUG=True`), emails are printed to the console instead of being sent. When you test the password reset:

1. Click "Forgot your password?" on the login page
2. Submit your email
3. Check the **Console/Terminal output** for the reset email with a link
4. Copy the link and open it in your browser

You can also test email delivery with the debug view:
```
http://127.0.0.1:8000/test-email/
```

This sends a test email to your account (only works when logged in, and only in debug mode).

---

## Production Setup (Gmail / Real SMTP)

To use real email sending in production, set these environment variables:

### Using Gmail:

```bash
DEBUG=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Use App Password, not Gmail password
DEFAULT_FROM_EMAIL=your-email@gmail.com
SERVER_EMAIL=your-email@gmail.com
```

**Note:** Gmail requires an "App Password" for SMTP. [See Google's guide](https://support.google.com/accounts/answer/185833)

### Using SendGrid:

```bash
DEBUG=False
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourapp.com
```

### Using Mailgun:

```bash
DEBUG=False
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=noreply@your-domain.mailgun.org
```

---

## How Password Reset Works

1. User clicks "Forgot your password?"
2. Enters email address
3. System sends password reset email with a secure token
4. User clicks link in email
5. Sets new password
6. Can log in with new password

The email contains a time-limited token (default: 3 days) that can only be used once.

---

## Testing in Development

- **View console output:** When `DEBUG=True`, reset links appear in the terminal
- **Test email endpoint:** Visit `/test-email/` to verify configuration
- **Check database:** Reset tokens are stored temporarily in Django's password reset table

---

## Security Notes

- Never commit real email credentials to version control
- Use environment variables for all sensitive keys
- In production, always use HTTPS
- Consider using a dedicated email service for reliability