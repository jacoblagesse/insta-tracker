from django import forms
from django.forms import ModelForm
from .models import User

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('_username', 'email')
        labels = {
            '_username': ('Instagram Username'),
            'email': ('Email'),
        }