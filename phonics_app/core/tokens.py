from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Email verification token that remains valid across login events.

    We intentionally avoid `last_login` in the hash so users can log in and still
    use a verification link that was sent earlier.
    """

    def _make_hash_value(self, user, timestamp):
        email = getattr(user, "email", "") or ""
        verified = getattr(user, "email_verified", False)
        return f"{user.pk}{timestamp}{verified}{email}"


email_verification_token = EmailVerificationTokenGenerator()
