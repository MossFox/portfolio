"""
URL configuration for fitness project.

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
from bookings import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("class_time_check/<int:TT_class_id>", views.class_time_check, name="class_time_check"),

    path("", views.index, name="index"),
    path("timetable/", views.timetable, name="timetable"),
    path("profile/", views.profile, name="profile"),
    path("date_update/", views.date_update, name="date_update"),
    path("placeholder_time_checker/", views.placeholder_time_checker, name="placeholder_time_checker"),
    path("PH_token/<int:class_id>", views.PH_token, name="PH_token"),

    path("booking", views.booking, name="booking"),
    path("teacher", views.teacher, name="teacher"),
    path("teacher_class/<str:action>", views.teacher_class, name="teacher_class"),
    path("teacher_check/<int:classId>", views.teacher_check, name="teacher_check"),
    path("teacher_delete/<int:classId>/<str:action>", views.teacher_delete, name="teacher_delete"),

    path("todo/", views.todo, name="todo"),
    path("club/<str:club>", views.club, name="club"),
    path("clear_session", views.clear_session, name='clear_session'),
    path("create_timetable", views.create_timetable, name="create_timetable"),
    path("notification_check", views.notification_check, name="notification_check"),
    path("notif_board", views.notif_board, name="notif_board"),


    path("get_clubs", views.get_clubs, name="get_clubs"),
    path('get_classes/<int:select_club>/', views.get_classes, name='get_classes'),
    path('get_days/<int:select_club>/<int:select_class>/', views.get_days, name='get_days'),
    path('get_time/<int:select_club>/<int:select_class>/<str:select_day>', views.get_time, name='get_time'),
    path('book/<int:classId>/<str:action>', views.book, name='book'),
    path('cancel/<int:classId>', views.cancel, name='cancel'),
    path("join_class", views.join_class, name="join_class"),
    path("fav/<int:classId>/<str:action>", views.favorites, name="favorites"),
    path("in_favorites/<int:classId>", views.in_favorites, name="in_favorites"),

    path("waitinglist/<int:classId>/<str:action>", views.waitinglist, name="waitinglist"),
    path("on_waitinglist/<int:classId>", views.on_waitinglist, name="on_waitinglist"),

]
