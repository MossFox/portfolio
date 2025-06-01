
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path('posts/', views.posts, name="posts"),
    path("post_edit/<int:post_id>", views.post_edit, name="edit"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("following", views.following, name="following"),
    path("new_post", views.new_post, name="new_post"),
    path("like/<int:post_id>", views.like, name="like"),
]
