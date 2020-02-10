from django.shortcuts import render, get_object_or_404
from django.views import generic
from .forms import InstaUserForm, SignUpForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import InstaUser
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
from django.contrib.auth import authenticate , login
from django.core import management
from .utils import follow_user
import django_rq
from redis import Redis
from .worker import conn
import instaloader
import time
import logging
from django.conf import settings

INSTAGRAM_USERNAME = settings.INSTAGRAM_USERNAME
INSTAGRAM_PASSWORD = settings.INSTAGRAM_PASSWORD

logger=logging.getLogger(__name__)
L = instaloader.Instaloader()

def initialview(request): 
    if request.method == 'POST': 
        form = InstaUserForm(request.POST, request.FILES) 

        if form.is_valid():
            data = form.cleaned_data
            
            L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')
            
            username = data['username']
            email = data['email']
            request.session['username'] = username
            request.session['email'] = email

            instauser, created = InstaUser.objects.update_or_create(username=username, email=email)

            logger.debug(instauser.username)

            #follow_user(instauser.username)
            queue = django_rq.get_queue('default')
            queue.enqueue(follow_user, instauser.username)

            return HttpResponseRedirect('/success')
    else: 
        form = InstaUserForm() 
    return render(request, 'followtracker/initial.html', {'form' : form})

class Success(TemplateView):
    template_name = 'followtracker/success.html'

#@login_required
class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('success')
    template_name = 'followtracker/signup.html'

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, initial={'username': request.session['username'], 'email': request.session['email']})
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user, password=raw_password)
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = SignUpForm(initial={'username': request.session['username'], 'email': request.session['email']})
    return render(request, 'followtracker/signup.html', {'form': form}) 
