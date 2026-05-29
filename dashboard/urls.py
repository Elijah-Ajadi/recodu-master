from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("users/", views.users, name="users"),
    path("users/<int:pk>/toggle/", views.toggle_user, name="toggle_user"),
    path("corrections/<int:pk>/approve/", views.approve_correction, name="approve_correction"),
    path("users/<int:pk>/role/", views.change_role, name="change_role"),
    path("export/", views.export, name="export"),
]
