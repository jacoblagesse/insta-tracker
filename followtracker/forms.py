from django import forms
from django.forms import ModelForm
from .models import InstaUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper

class InstaUserForm(ModelForm):
    class Meta:
        model = InstaUser
        fields = ('username', 'email')
        labels = {
            'username': '',
            'email': '',
        }

    def __init__(self, *args, **kwargs):
        super(InstaUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Instagram Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].disabled = True
        self.fields['email'].disabled = True
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

        self.helper = FormHelper(self)
        self.helper.form_show_errors = False