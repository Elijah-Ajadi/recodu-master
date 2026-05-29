from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path("search/", views.search, name="search"),
    path("api/search/", views.ajax_search, name="ajax_search"),
    path("api/create/", views.create, name="create"),
    path("<int:pk>/", views.profile, name="profile"),
    path("<int:pk>/edit/", views.edit_profile, name="edit_profile"),
    path("<int:pk>/history/", views.history, name="history"),
]
