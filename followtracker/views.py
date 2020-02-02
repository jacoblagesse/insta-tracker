from django.shortcuts import render, get_object_or_404
from django.views import generic
from .forms import UserForm
from django.urls import reverse_lazy
from .models import User
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
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

def signupview(request): 
    if request.method == 'POST': 
        form = UserForm(request.POST, request.FILES) 

        if form.is_valid():
            data = form.cleaned_data
            
            L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            
            username = data['username']
            email = data['email']
            user, created = User.objects.update_or_create(username=username, email=email)
            #form.save()

            logger.debug(user.username)

            queue = django_rq.get_queue('default')
            queue.enqueue(follow_user, user.username)

            return HttpResponseRedirect('/success')
    else: 
        form = UserForm() 
    return render(request, 'followtracker/signup.html', {'form' : form})

class Success(TemplateView):
    template_name = 'followtracker/success.html'