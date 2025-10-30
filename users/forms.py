from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=False, label="First name", max_length=100)
    last_name = forms.CharField(required=False, label="Last name", max_length=100)
    bio = forms.CharField(required=False, label="Bio", widget=forms.Textarea, max_length=1000)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "bio"

        ]

    def save(self, commit = True):
        user = super().save(commit = False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.bio = self.cleaned_data["bio"]

        if commit:
            user.save()

        return user
    
class LoginForm(forms.Form):
    identifier = forms.CharField(label="Username or Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Password"}), required=True)

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier")
        password = cleaned_data.get("password")
        if identifier and password:
            user = User.objects.filter(username=identifier).first()

            if not user:
                user = User.objects.filter(email=identifier).first()

            if not user:
                raise forms.ValidationError("Invalid username/email")
            
            if not user.check_password(password):
                raise forms.ValidationError("Invalid password.")

            if not user.is_active:
                raise forms.ValidationError("User is not active. Check your inbox")
            

            cleaned_data["user"] = user
        return cleaned_data