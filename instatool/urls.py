from django.contrib import admin
from django.urls import path
from followtracker import views
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.initialview, name='initial'),
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls'), name='login'),
    path('success/', views.Success.as_view(), name='success'),
    path('django-rq/', include('django_rq.urls')),
]