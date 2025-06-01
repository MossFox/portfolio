from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("checklist", views.checklist, name="checklist"),
    path("search", views.search, name="s_name"),
    path("new", views.new_entry, name="new_entry"),
    path("edit", views.edit, name="edit"),
    path("rand", views.rand, name="rand"),
    path("wiki/<str:name>", views.entry, name="entry") #has to be last or it causes issue. dynamic path that automatically jumps in
]
