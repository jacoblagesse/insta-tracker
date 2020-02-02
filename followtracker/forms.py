from django import forms
from django.forms import ModelForm
from .models import User

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': '',
            'email': '',
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Instagram Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'