from django.shortcuts import render, get_object_or_404
from django.views import generic
from .forms import UserForm
from django.urls import reverse_lazy
from .models import User
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
from django.core import management
from .utils import get_full_data
from rq import Queue
from redis import Redis
from .worker import conn
import time
import logging

logger=logging.getLogger(__name__)

class SignUp(generic.CreateView):
    form_class = UserForm
    success_url = reverse_lazy('success')
    template_name = 'followtracker/signup.html'

def signupview(request): 
    if request.method == 'POST': 
        form = UserForm(request.POST, request.FILES) 
        #logger.error(request.user._username)
        if form.is_valid(): 
            user = form.save(commit=False)
            form.save()
            logger.debug(user._username)
            q = Queue(connection=conn)
            q.enqueue(get_full_data, user._username)
            return HttpResponseRedirect('/success')
    else: 
        form = UserForm() 
    return render(request, 'followtracker/signup.html', {'form' : form})

class Success(TemplateView):
    template_name = 'followtracker/success.html'