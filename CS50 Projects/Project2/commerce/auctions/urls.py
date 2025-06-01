from django.urls import path

from . import views

urlpatterns = [
    path("checklist", views.checklist, name="checklist"),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("categories/<str:category_name>/", views.category, name="category"),
    path("<str:listing_name>/", views.listing, name="listing"),
]
