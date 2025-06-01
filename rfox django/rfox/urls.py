"""
URL configuration for rfox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from resting import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name = "index"),
    path('about/', views.about, name = "about"),
    path('contact/', views.contact, name = "contact"),
    path('forgot/', views.forgot, name = "forgot"),
    path('login/', views.login_view, name = "login"),
    path('logout/', views.logout_view, name = "logout"),
    path('register/', views.register, name = "register"),
    path('reset/', views.reset, name = "reset"),
    path('pass_change/', views.pass_change, name = "pass_change"),
    path('massage/', views.massage, name = "massage"),
    path('admin_page/', views.admin_page, name = "admin_page"),
    path('schedule/', views.schedule, name = "schedule"),
    path('verify/', views.verify, name = "verify"),
    path('gift/', views.gift, name = "gift"),
    path('get_times/', views.get_times, name = "get_times"),
    path('actions/', views.actions, name = "actions"),

]

