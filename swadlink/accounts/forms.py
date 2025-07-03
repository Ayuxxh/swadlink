from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally customize placeholders or widgets here
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Enter password'})