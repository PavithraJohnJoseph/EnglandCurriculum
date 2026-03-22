from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Plan, User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)

        # Ensure new users have an initial plan associated in backend details.
        if not user.plan:
            default_plan = Plan.objects.filter(is_free=True).order_by("price", "id").first()
            if default_plan:
                user.plan = default_plan

        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email address is already registered. Please use a "
                "different email or try logging in."
            )
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose a different username."
            )
        return username


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",  # Disable browser autofill
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "off",  # Disable browser autofill
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure fields are always blank initially
        # Note: Cookie-based auto-population can be added here later if needed
        self.fields["username"].initial = ""
        self.fields["password"].initial = ""
